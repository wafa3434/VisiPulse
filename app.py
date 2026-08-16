"""
VisiPulse - نظام المراقبة الاستباقية لإدارة الصحة الإلكترونية
نسخة مُعدَّة بممارسات إنتاجية (Production-grade code practices).

مهم جداً: هذا الملف يرفع جاهزية الكود هندسياً، لكنه ليس بديلاً عن:
  - تدقيق أمني واختبار اختراق مستقل قبل أي ربط بأجهزة طبية فعلية
  - اعتماد الامتثال التنظيمي (PDPL / NCA-ECC / متطلبات الجهة الصحية)
  - ربط فعلي بمزود هوية مؤسسي (LDAP/AD/SSO) بدل جدول المستخدمين المحلي
  - تكامل حقيقي مع أدوات مراقبة الشبكة والأجهزة (انظر live_source.py)
راجع ملف DEPLOYMENT_CHECKLIST.md المرفق قبل أي نشر فعلي.
"""

from __future__ import annotations

import logging
import os
import random
import uuid
from contextlib import closing
from datetime import datetime, timedelta

import bcrypt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# ---------------------------------------------------------------------------
# الإعدادات (كلها عبر متغيرات بيئة - لا أسرار داخل الكود)
# ---------------------------------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("VISIPULSE_DB_URL", "sqlite:///visipulse.db")
MAX_LOGIN_ATTEMPTS = int(os.getenv("VISIPULSE_MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_MINUTES = int(os.getenv("VISIPULSE_LOCKOUT_MINUTES", "15"))
SESSION_IDLE_TIMEOUT_MIN = int(os.getenv("VISIPULSE_SESSION_TIMEOUT_MIN", "30"))
LOG_FILE = os.getenv("VISIPULSE_LOG_FILE", "visipulse.log")
FORCE_PASSWORD_CHANGE_ON_SEED = os.getenv("VISIPULSE_FORCE_PW_CHANGE", "true").lower() == "true"

SLA_HOURS_BY_PRIORITY = {"عاجلة": 2, "عالية": 8, "عادية": 24}

# ---------------------------------------------------------------------------
# التسجيل (Logging) - يفصل السجل التشغيلي عن سجل التدقيق داخل القاعدة
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("visipulse")

# ---------------------------------------------------------------------------
# طبقة قاعدة البيانات (SQLAlchemy: تعمل مع SQLite للتطوير و PostgreSQL للإنتاج
# بدون تغيير أي سطر آخر في الكود - فقط بتغيير VISIPULSE_DB_URL)
# ---------------------------------------------------------------------------
_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
        _engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    return _engine


def init_db():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                must_change_password BOOLEAN NOT NULL DEFAULT 1,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                locked_until TEXT,
                is_active BOOLEAN NOT NULL DEFAULT 1
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                closed_at TEXT,
                department TEXT NOT NULL,
                device_name TEXT NOT NULL,
                location TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                issue_desc TEXT,
                priority TEXT NOT NULL DEFAULT 'عادية',
                status TEXT NOT NULL DEFAULT 'مفتوحة',
                created_by TEXT,
                closed_by TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                related_ticket_id TEXT,
                decision_text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'معتمد للتنفيذ',
                created_by TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS maintenance_dispatches (
                dispatch_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                related_ticket_id TEXT,
                contractor_name TEXT NOT NULL,
                fault_description TEXT NOT NULL,
                created_by TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id TEXT PRIMARY KEY,
                ts TEXT NOT NULL,
                username TEXT,
                action TEXT NOT NULL,
                details TEXT
            )
        """))

    # مستخدمون أوليون فقط عند عدم وجود أي مستخدم - كلمات مرور عشوائية تُطبع
    # مرة واحدة في السجل، وتُجبر على التغيير عند أول دخول. لا كلمات مرور
    # ثابتة معروفة مسبقاً كما في نسخة العرض التصويري.
    with engine.begin() as conn:
        existing = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if existing == 0:
            seed_roles = [
                ("admin", "مدير النظام (يُنشئ بقية الحسابات)", "system_admin"),
            ]
            for uname, fname, role in seed_roles:
                temp_password = uuid.uuid4().hex[:12]
                conn.execute(
                    text("""INSERT INTO users
                            (username, password_hash, full_name, role, must_change_password)
                            VALUES (:u, :p, :f, :r, :m)"""),
                    {"u": uname, "p": hash_password(temp_password), "f": fname,
                     "r": role, "m": FORCE_PASSWORD_CHANGE_ON_SEED},
                )
                # كلمة المرور المؤقتة تُطبع في السجل الآمن فقط (وليست في الشاشة أو الكود)
                # ليطّلع عليها المسؤول عن النشر الأولي ثم يسلّمها بقناة آمنة (لا عبر Slack/Email عادي).
                logger.warning("SEED USER CREATED username=%s temp_password=%s (must change on first login)",
                                uname, temp_password)


# ---------------------------------------------------------------------------
# كلمات المرور: bcrypt (salt تلقائي لكل مستخدم، عامل تكلفة قابل للتهيئة)
# ---------------------------------------------------------------------------
def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def check_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # هاش تالف أو غير متوافق - يُعامل كفشل تحقق ولا يُسقط التطبيق
        return False


def verify_login(username: str, password: str):
    """يتحقق من الهوية مع قفل الحساب بعد محاولات فاشلة متكررة (Brute-force mitigation)."""
    username = username.strip()
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT * FROM users WHERE username = :u"), {"u": username}
        ).mappings().fetchone()

        if not row or not row["is_active"]:
            log_action(username, "محاولة دخول فاشلة", "مستخدم غير موجود أو معطّل")
            return None, "بيانات الدخول غير صحيحة."

        if row["locked_until"]:
            locked_until = datetime.fromisoformat(row["locked_until"])
            if datetime.now() < locked_until:
                remaining = int((locked_until - datetime.now()).total_seconds() // 60) + 1
                return None, f"الحساب مقفل مؤقتاً. حاول بعد {remaining} دقيقة."

        if check_password(password, row["password_hash"]):
            conn.execute(
                text("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = :u"),
                {"u": username},
            )
            log_action(username, "تسجيل دخول ناجح")
            return dict(row), None

        attempts = row["failed_attempts"] + 1
        lock_sql = "UPDATE users SET failed_attempts = :a"
        params = {"a": attempts, "u": username}
        if attempts >= MAX_LOGIN_ATTEMPTS:
            lock_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
            lock_sql += ", locked_until = :l"
            params["l"] = lock_until.isoformat()
            log_action(username, "قفل الحساب", f"بعد {attempts} محاولات فاشلة")
        lock_sql += " WHERE username = :u"
        conn.execute(text(lock_sql), params)
        log_action(username, "محاولة دخول فاشلة", f"المحاولة رقم {attempts}")
        return None, "بيانات الدخول غير صحيحة."


def change_password(username: str, new_password: str):
    ok, msg = validate_password_policy(new_password)
    if not ok:
        return False, msg
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET password_hash = :p, must_change_password = 0 WHERE username = :u"),
            {"p": hash_password(new_password), "u": username},
        )
    log_action(username, "تغيير كلمة المرور")
    return True, "تم تحديث كلمة المرور بنجاح."


def validate_password_policy(pw: str):
    if len(pw) < 10:
        return False, "يجب ألا تقل كلمة المرور عن 10 أحرف."
    if not any(c.isdigit() for c in pw):
        return False, "يجب أن تحتوي كلمة المرور على رقم واحد على الأقل."
    if not any(c.isupper() for c in pw) and not any(c.islower() for c in pw):
        return False, "يجب أن تحتوي كلمة المرور على أحرف."
    return True, ""


# ---------------------------------------------------------------------------
# سجل التدقيق
# ---------------------------------------------------------------------------
def log_action(username: str | None, action: str, details: str = ""):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO audit_log (log_id, ts, username, action, details)
                    VALUES (:id, :ts, :u, :a, :d)"""),
            {"id": str(uuid.uuid4()), "ts": datetime.now().isoformat(timespec="seconds"),
             "u": username, "a": action, "d": details},
        )
    logger.info("AUDIT user=%s action=%s details=%s", username, action, details)


# ---------------------------------------------------------------------------
# التحقق من صحة المدخلات (Input validation) - دفاع إضافي رغم استخدام
# استعلامات مُعامَلة (Parameterized) في كل مكان لمنع SQL Injection أصلاً
# ---------------------------------------------------------------------------
def sanitize_text(value: str, max_len: int = 500) -> str:
    value = (value or "").strip()
    return value[:max_len]


# ---------------------------------------------------------------------------
# عمليات التذاكر / القرارات / بلاغات الصيانة
# ---------------------------------------------------------------------------
def create_ticket(department, device_name, location, alert_type, issue_desc, priority, created_by):
    ticket_id = "TCK-" + uuid.uuid4().hex[:8].upper()
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO tickets
                    (ticket_id, created_at, department, device_name, location, alert_type,
                     issue_desc, priority, status, created_by)
                    VALUES (:tid, :ts, :dep, :dev, :loc, :typ, :desc, :pri, 'مفتوحة', :by)"""),
            {"tid": ticket_id, "ts": datetime.now().isoformat(timespec="seconds"),
             "dep": department, "dev": sanitize_text(device_name, 120),
             "loc": sanitize_text(location, 200), "typ": alert_type,
             "desc": sanitize_text(issue_desc, 500), "pri": priority, "by": created_by},
        )
    log_action(created_by, "إنشاء تذكرة", f"{ticket_id} -> {department}")
    return ticket_id


def close_ticket(ticket_id, closed_by):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE tickets SET status='مغلقة', closed_at=:ts, closed_by=:by WHERE ticket_id=:tid"),
            {"ts": datetime.now().isoformat(timespec="seconds"), "by": closed_by, "tid": ticket_id},
        )
    log_action(closed_by, "إغلاق تذكرة", ticket_id)


def get_tickets_df(department: str | None = None) -> pd.DataFrame:
    engine = get_engine()
    q = "SELECT * FROM tickets"
    params = {}
    if department:
        q += " WHERE department = :dep"
        params["dep"] = department
    q += " ORDER BY created_at DESC"
    with engine.begin() as conn:
        df = pd.read_sql_query(text(q), conn, params=params)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["sla_deadline"] = df.apply(
            lambda r: r["created_at"] + timedelta(hours=SLA_HOURS_BY_PRIORITY.get(r["priority"], 24)), axis=1
        )
        now = datetime.now()
        df["متأخرة عن SLA؟"] = df.apply(
            lambda r: "نعم ⚠️" if (r["status"] == "مفتوحة" and now > r["sla_deadline"]) else "لا", axis=1
        )
    return df


def add_decision(related_ticket_id, decision_text_val, created_by):
    decision_id = "DEC-" + uuid.uuid4().hex[:8].upper()
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO decisions
                    (decision_id, created_at, related_ticket_id, decision_text, status, created_by)
                    VALUES (:id, :ts, :rid, :txt, 'معتمد للتنفيذ', :by)"""),
            {"id": decision_id, "ts": datetime.now().isoformat(timespec="seconds"),
             "rid": related_ticket_id, "txt": sanitize_text(decision_text_val, 1000), "by": created_by},
        )
    log_action(created_by, "إضافة قرار إداري", f"{decision_id} مرتبط بـ {related_ticket_id or 'بدون تذكرة'}")
    return decision_id


def get_decisions_df() -> pd.DataFrame:
    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql_query(text("SELECT * FROM decisions ORDER BY created_at DESC"), conn)


def add_dispatch(related_ticket_id, contractor_name, fault_description, created_by):
    dispatch_id = "DSP-" + uuid.uuid4().hex[:8].upper()
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO maintenance_dispatches
                    (dispatch_id, created_at, related_ticket_id, contractor_name, fault_description, created_by)
                    VALUES (:id, :ts, :rid, :c, :f, :by)"""),
            {"id": dispatch_id, "ts": datetime.now().isoformat(timespec="seconds"),
             "rid": related_ticket_id, "c": sanitize_text(contractor_name, 200),
             "f": sanitize_text(fault_description, 500), "by": created_by},
        )
    log_action(created_by, "إرسال بلاغ لشركة مقاولة", f"{dispatch_id} -> {contractor_name}")
    return dispatch_id


def get_dispatches_df() -> pd.DataFrame:
    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql_query(text("SELECT * FROM maintenance_dispatches ORDER BY created_at DESC"), conn)


# ---------------------------------------------------------------------------
# مصدر القراءات الحية - انظر live_source.py لواجهة التكامل الحقيقي
# ---------------------------------------------------------------------------
from live_source import get_live_reading  # noqa: E402  (يبقى في الأسفل عمداً بعد تعريف الدوال المساعدة)


# ---------------------------------------------------------------------------
# إعداد الصفحة والحالة
# ---------------------------------------------------------------------------
st.set_page_config(page_title="VisiPulse - E-Health Proactive Monitoring System",
                    layout="wide", initial_sidebar_state="expanded")
init_db()

if "user" not in st.session_state:
    st.session_state.user = None
if "last_activity" not in st.session_state:
    st.session_state.last_activity = datetime.now()
if "current_alert" not in st.session_state:
    st.session_state.current_alert = get_live_reading()

# انتهاء الجلسة تلقائياً عند عدم النشاط (مهم لبيئة مشتركة داخل المستشفى)
if st.session_state.user is not None:
    idle_minutes = (datetime.now() - st.session_state.last_activity).total_seconds() / 60
    if idle_minutes > SESSION_IDLE_TIMEOUT_MIN:
        log_action(st.session_state.user["username"], "إنهاء جلسة تلقائي", "بسبب عدم النشاط")
        st.session_state.user = None
        st.warning("تم إنهاء الجلسة تلقائياً بسبب عدم النشاط. يرجى تسجيل الدخول مرة أخرى.")
    else:
        st.session_state.last_activity = datetime.now()

ROLE_LABELS = {
    "system_admin": "مدير النظام",
    "employee": "موظف ميداني",
    "it_support": "موظف الدعم الفني",
    "it_systems": "موظف الأنظمة والتطبيقات",
    "it_infra": "موظف البنية التحتية",
    "quality_mgr": "مدير الجودة",
    "ehealth_mgr": "مدير الصحة الإلكترونية",
    "top_mgmt": "الإدارة العليا",
}
ROLE_TO_DEPARTMENT = {
    "it_support": "قسم الدعم الفني",
    "it_systems": "قسم الأنظمة والتطبيقات",
    "it_infra": "قسم البنية التحتية",
}


def login_screen():
    st.markdown("<h2 style='text-align:center;color:#1a5276;'>VisiPulse - تسجيل الدخول</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول", use_container_width=True):
            if not username or not password:
                st.error("يرجى تعبئة اسم المستخدم وكلمة المرور.")
            else:
                user, err = verify_login(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.last_activity = datetime.now()
                    st.rerun()
                else:
                    st.error(err)
        st.caption(
            "لا توجد حسابات تجريبية في هذه النسخة. يُنشئ حساب admin عند أول تشغيل "
            "بكلمة مرور عشوائية مؤقتة تُكتب في ملف السجل (visipulse.log) فقط."
        )


if st.session_state.user is None:
    login_screen()
    st.stop()

user = st.session_state.user
role = user["role"]

# إجبار تغيير كلمة المرور عند أول دخول بحساب مبذور (seed)
if user.get("must_change_password"):
    st.warning("يجب تعيين كلمة مرور جديدة قبل المتابعة.")
    new_pw = st.text_input("كلمة المرور الجديدة", type="password", key="pw1")
    new_pw2 = st.text_input("تأكيد كلمة المرور الجديدة", type="password", key="pw2")
    if st.button("تحديث كلمة المرور"):
        if new_pw != new_pw2:
            st.error("كلمتا المرور غير متطابقتين.")
        else:
            ok, msg = change_password(user["username"], new_pw)
            if ok:
                st.success(msg + " يرجى تسجيل الدخول من جديد.")
                st.session_state.user = None
            else:
                st.error(msg)
    st.stop()

# ---------------------------------------------------------------------------
# الترويسة
# ---------------------------------------------------------------------------
h1, h2, h3 = st.columns([1, 6, 2])
with h1:
    logo_path = os.getenv("VISIPULSE_LOGO_PATH", "logo.jpeg")
    if os.path.exists(logo_path):
        st.image(logo_path, width=110)
    else:
        st.markdown("**تجمع صحي**")
with h2:
    st.markdown(
        "<h2 style='text-align:center;color:#1a5276;margin-bottom:0;'>VisiPulse - نظام المراقبة الاستباقية</h2>"
        f"<p style='text-align:center;color:#555;font-size:14px;'>مسجّل الدخول: {user['full_name']} ({ROLE_LABELS.get(role, role)})</p>",
        unsafe_allow_html=True,
    )
with h3:
    if st.button("تسجيل الخروج"):
        log_action(user["username"], "تسجيل خروج")
        st.session_state.user = None
        st.rerun()

st.markdown("---")

# ---------------------------------------------------------------------------
# شاشة الموظف الميداني
# ---------------------------------------------------------------------------
if role == "employee":
    st.subheader("لوحة التنبيهات الاستباقية الفورية")
    alert = st.session_state.current_alert
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("اسم الجهاز", alert["device_name"])
    c2.metric("الموقع", alert["location"])
    c3.metric("نوع التنبيه", alert["alert_type"])
    c4.metric("الأولوية المقترحة", alert["priority"])
    st.error(f"حالة الإنذار: {alert['issue_desc']}")

    if st.button("موافق (OK) - إرسال البلاغ تلقائياً"):
        target_dept = "قسم الأنظمة والتطبيقات" if alert["alert_type"] == "تقني" else "قسم الدعم الفني"
        tid = create_ticket(target_dept, alert["device_name"], alert["location"],
                             alert["alert_type"], alert["issue_desc"], alert["priority"], user["username"])
        st.success(f"تم إرسال البلاغ بنجاح. رقم التذكرة: {tid}")
        st.session_state.current_alert = get_live_reading()
        st.rerun()

# ---------------------------------------------------------------------------
# شاشة الإدارة العليا
# ---------------------------------------------------------------------------
elif role == "top_mgmt":
    st.subheader("لوحة مؤشرات الأداء الاستراتيجية")
    df = get_tickets_df()
    total = len(df)
    closed = len(df[df["status"] == "مغلقة"]) if total else 0
    overdue = len(df[df["متأخرة عن SLA؟"] == "نعم ⚠️"]) if total else 0
    closure_rate = (closed / total * 100) if total else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("إجمالي التذاكر المسجلة", total)
    k2.metric("نسبة إغلاق التذاكر", f"{closure_rate:.1f}%")
    k3.metric("تذاكر متأخرة عن SLA", overdue)
    k4.metric("القرارات الإدارية الموثقة", len(get_decisions_df()))

    if total:
        st.write("توزيع التذاكر حسب القسم:")
        st.bar_chart(df["department"].value_counts())
        st.write("توزيع التذاكر حسب الأولوية:")
        st.bar_chart(df["priority"].value_counts())
    else:
        st.info("لا توجد بيانات كافية بعد.")

    with st.expander("سجل التدقيق - آخر 50 عملية"):
        engine = get_engine()
        with engine.begin() as conn:
            audit_df = pd.read_sql_query(text("SELECT * FROM audit_log ORDER BY ts DESC LIMIT 50"), conn)
        st.dataframe(audit_df, use_container_width=True)

# ---------------------------------------------------------------------------
# أقسام IT التخصصية
# ---------------------------------------------------------------------------
elif role in ("it_support", "it_systems", "it_infra"):
    dept_name = ROLE_TO_DEPARTMENT[role]
    st.subheader(f"واجهة {ROLE_LABELS[role]}")
    df = get_tickets_df(dept_name)

    if not df.empty:
        st.dataframe(df[["ticket_id", "created_at", "device_name", "location", "alert_type",
                          "priority", "status", "متأخرة عن SLA؟"]], use_container_width=True)
        open_tickets = df[df["status"] == "مفتوحة"]
        if not open_tickets.empty:
            to_close = st.selectbox("اختر تذكرة لإغلاقها:", open_tickets["ticket_id"].tolist())
            if st.button("إغلاق التذكرة المحددة"):
                close_ticket(to_close, user["username"])
                st.success(f"تم إغلاق التذكرة {to_close}.")
                st.rerun()
    else:
        st.info("لا توجد بلاغات معلقة لهذا القسم حالياً.")

    if role == "it_support":
        st.markdown("---")
        st.subheader("إرسال بلاغ صيانة إلى شركة مقاولة")
        with st.form("dispatch_form"):
            options = ["بدون ربط"] + (df["ticket_id"].tolist() if not df.empty else [])
            related = st.selectbox("التذكرة المرتبطة (اختياري):", options)
            contractor = st.text_input("اسم الشركة المقاولة")
            fault = st.text_input("وصف العطل")
            if st.form_submit_button("إرسال البلاغ"):
                if contractor and fault:
                    rid = None if related == "بدون ربط" else related
                    did = add_dispatch(rid, contractor, fault, user["username"])
                    st.success(f"تم إرسال البلاغ ({did}) إلى {contractor}.")
                else:
                    st.warning("يرجى تعبئة اسم الشركة ووصف العطل.")
        dispatches = get_dispatches_df()
        if not dispatches.empty:
            st.dataframe(dispatches, use_container_width=True)

# ---------------------------------------------------------------------------
# مدير الجودة
# ---------------------------------------------------------------------------
elif role == "quality_mgr":
    st.subheader("واجهة مدير الجودة")
    df = get_tickets_df()
    if not df.empty:
        closure_rate = len(df[df["status"] == "مغلقة"]) / len(df) * 100
        overdue = len(df[df["متأخرة عن SLA؟"] == "نعم ⚠️"])
        c1, c2 = st.columns(2)
        c1.metric("نسبة إغلاق البلاغات الفعلية", f"{closure_rate:.1f}%")
        c2.metric("تذاكر متأخرة عن SLA", overdue)
        st.bar_chart(df["department"].value_counts())
    else:
        st.info("لا توجد بيانات كافية بعد.")

    st.markdown("---")
    st.subheader("تدوين قرار إداري تصحيحي (مرتبط بالتذكرة المسبِّبة)")
    with st.form("decision_form"):
        ticket_options = ["بدون ربط بتذكرة"] + (df["ticket_id"].tolist() if not df.empty else [])
        related_ticket = st.selectbox("التذكرة أو الحادثة ذات الصلة:", ticket_options)
        decision_text_val = st.text_area("نص القرار الإداري أو التوصية:")
        if st.form_submit_button("حفظ القرار"):
            if decision_text_val:
                rid = None if related_ticket == "بدون ربط بتذكرة" else related_ticket
                did = add_decision(rid, decision_text_val, user["username"])
                st.success(f"تم حفظ القرار {did}.")
            else:
                st.warning("يرجى كتابة نص القرار.")

    decisions_df = get_decisions_df()
    if not decisions_df.empty:
        st.write("سجل القرارات الإدارية الموثّقة:")
        st.dataframe(decisions_df, use_container_width=True)

# ---------------------------------------------------------------------------
# مدير الصحة الإلكترونية
# ---------------------------------------------------------------------------
elif role == "ehealth_mgr":
    st.subheader("واجهة إدارة الصحة الإلكترونية")
    df = get_tickets_df()
    if not df.empty:
        st.dataframe(df[["ticket_id", "created_at", "department", "device_name",
                          "priority", "status", "متأخرة عن SLA؟"]], use_container_width=True)
        st.bar_chart(df.groupby("department")["ticket_id"].count())
    else:
        st.info("لا توجد بيانات كافية بعد.")
    st.caption(
        "الربط الفعلي بأنظمة PACS/LIS/الملف الطبي الإلكتروني يتطلب واجهات برمجية "
        "من مزوّديها ولم يُفعَّل بعد."
    )

# ---------------------------------------------------------------------------
# مدير النظام (لإدارة المستخدمين - لا كلمات مرور موحدة بعد الآن)
# ---------------------------------------------------------------------------
elif role == "system_admin":
    st.subheader("إدارة المستخدمين")
    with st.form("create_user_form"):
        new_username = st.text_input("اسم المستخدم الجديد")
        new_fullname = st.text_input("الاسم الكامل")
        new_role = st.selectbox("الدور الوظيفي", [r for r in ROLE_LABELS if r != "system_admin"],
                                 format_func=lambda r: ROLE_LABELS[r])
        if st.form_submit_button("إنشاء المستخدم"):
            temp_pw = uuid.uuid4().hex[:12]
            engine = get_engine()
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("""INSERT INTO users (username, password_hash, full_name, role, must_change_password)
                                VALUES (:u, :p, :f, :r, 1)"""),
                        {"u": sanitize_text(new_username, 50), "p": hash_password(temp_pw),
                         "f": sanitize_text(new_fullname, 120), "r": new_role},
                    )
                log_action(user["username"], "إنشاء مستخدم", new_username)
                st.success(f"تم إنشاء المستخدم. كلمة المرور المؤقتة: {temp_pw} — سلّمها بقناة آمنة، لن تُعرض مرة أخرى.")
            except Exception as e:  # يشمل تكرار اسم المستخدم (unique constraint)
                logger.error("فشل إنشاء مستخدم: %s", e)
                st.error("تعذّر إنشاء المستخدم (قد يكون الاسم مستخدماً مسبقاً).")

    engine = get_engine()
    with engine.begin() as conn:
        users_df = pd.read_sql_query(
            text("SELECT username, full_name, role, is_active, locked_until FROM users"), conn
        )
    st.dataframe(users_df, use_container_width=True)
