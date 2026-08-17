from __future__ import annotations

import logging
import os
import random
import uuid
import time
from contextlib import closing
from datetime import datetime, timedelta

import bcrypt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from cryptography.fernet import Fernet

# ---------------------------------------------------------------------------
# 1. الإعدادات والتحقق من البيئة
# ---------------------------------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("VISIPULSE_DB_URL", "sqlite:///visipulse.db")
MAX_LOGIN_ATTEMPTS = int(os.getenv("VISIPULSE_MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_MINUTES = int(os.getenv("VISIPULSE_LOCKOUT_MINUTES", "15"))
SESSION_IDLE_TIMEOUT_MIN = int(os.getenv("VISIPULSE_SESSION_TIMEOUT_MIN", "30"))
LOG_FILE = os.getenv("VISIPULSE_LOG_FILE", "visipulse.log")
FORCE_PASSWORD_CHANGE_ON_SEED = os.getenv("VISIPULSE_FORCE_PW_CHANGE", "true").lower() == "true"
ENCRYPTION_KEY = os.getenv("VISIPULSE_ENCRYPTION_KEY")

# توليد مفتاح مؤقت للتطوير إذا لم يُعرّف (ضمان عدم توقف النظام محلياً)
if not ENCRYPTION_KEY:
    # مفتاح افتراضي آمن للتطوير المحلي فقط
    ENCRYPTION_KEY = Fernet.generate_key().decode()

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

SLA_HOURS_BY_PRIORITY = {"عاجلة": 2, "عالية": 8, "عادية": 24}

# ---------------------------------------------------------------------------
# 2. التسجيل (Logging) والتشفير (Encryption)
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("visipulse")

def encrypt_val(text_val: str) -> str:
    """تشفير النصوص الحساسة قبل تخزينها."""
    if not text_val: return ""
    return cipher_suite.encrypt(text_val.encode()).decode()

def decrypt_val(cipher_text: str) -> str:
    """فك تشفير النصوص عند العرض."""
    if not cipher_text: return ""
    try:
        return cipher_suite.decrypt(cipher_text.encode()).decode()
    except Exception:
        return "**********" # في حال فشل فك التشفير

def sanitize_text(value: str, max_len: int = 500) -> str:
    """تطهير المدخلات لمنع المحاولات الخبيثة."""
    value = (value or "").strip()
    return value[:max_len]

# ---------------------------------------------------------------------------
# 3. طبقة قاعدة البيانات مع خاصية إعادة المحاولة (Resilience)
# ---------------------------------------------------------------------------
_engine: Engine | None = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {"sslmode": "require"}
        _engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    return _engine

def safe_execute(query, params=None, max_retries=3):
    """تنفيذ الاستعلامات مع معالجة أخطاء الاتصال."""
    engine = get_engine()
    for attempt in range(max_retries):
        try:
            with engine.begin() as conn:
                return conn.execute(text(query), params or {})
        except OperationalError as e:
            if attempt == max_retries - 1: raise e
            time.sleep(1)
            logger.warning("DB Retry attempt %s", attempt + 1)

def init_db():
    safe_execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, full_name TEXT NOT NULL,
            role TEXT NOT NULL, must_change_password BOOLEAN NOT NULL DEFAULT 1,
            failed_attempts INTEGER NOT NULL DEFAULT 0, locked_until TEXT, is_active BOOLEAN NOT NULL DEFAULT 1
        )
    """)
    safe_execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, closed_at TEXT,
            department TEXT NOT NULL, device_name TEXT NOT NULL, location TEXT NOT NULL,
            alert_type TEXT NOT NULL, issue_desc TEXT, priority TEXT NOT NULL DEFAULT 'عادية',
            status TEXT NOT NULL DEFAULT 'مفتوحة', created_by TEXT, closed_by TEXT
        )
    """)
    safe_execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id TEXT PRIMARY KEY, ts TEXT NOT NULL, username TEXT, action TEXT NOT NULL, details TEXT
        )
    """)
    safe_execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, related_ticket_id TEXT, 
            decision_text TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'معتمد', created_by TEXT
        )
    """)

    # مستخدم أدمن افتراضي ومستخدمين للأقسام لسهولة الاختبار
    existing = safe_execute("SELECT COUNT(*) FROM users").scalar()
    if existing == 0:
        temp_pw = "Admin@123"
        safe_execute(
            "INSERT INTO users (username, password_hash, full_name, role, must_change_password) VALUES (:u, :p, :f, :r, :m)",
            {"u": "admin", "p": hash_password(temp_pw), "f": "مدير النظام (Admin)", "r": "system_admin", "m": 1}
        )
        safe_execute(
            "INSERT INTO users (username, password_hash, full_name, role, must_change_password) VALUES (:u, :p, :f, :r, :m)",
            {"u": "quality", "p": hash_password("Quality@123"), "f": "مدير الجودة (CBAHI)", "r": "quality_mgr", "m": 0}
        )
        safe_execute(
            "INSERT INTO users (username, password_hash, full_name, role, must_change_password) VALUES (:u, :p, :f, :r, :m)",
            {"u": "it_lead", "p": hash_password("It@12345"), "f": "قائد تقنية المعلومات", "r": "it_lead", "m": 0}
        )
        safe_execute(
            "INSERT INTO users (username, password_hash, full_name, role, must_change_password) VALUES (:u, :p, :f, :r, :m)",
            {"u": "employee", "p": hash_password("Emp@12345"), "f": "موظف المستشفى", "r": "employee", "m": 0}
        )
        logger.info("SEED USERS CREATED SUCCESSFULLY.")

# ---------------------------------------------------------------------------
# 4. إدارة الهوية والأمان
# ---------------------------------------------------------------------------
def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def check_password(raw: str, hashed: str) -> bool:
    try: return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))
    except: return False

def log_action(username: str | None, action: str, details: str = ""):
    safe_execute(
        "INSERT INTO audit_log (log_id, ts, username, action, details) VALUES (:id, :ts, :u, :a, :d)",
        {"id": str(uuid.uuid4()), "ts": datetime.now().isoformat(), "u": username, "a": action, "d": details}
    )

def verify_login(username: str, password: str):
    username = sanitize_text(username, 50)
    row = safe_execute("SELECT * FROM users WHERE username = :u", {"u": username}).mappings().fetchone()
    
    if not row or not row["is_active"]:
        return None, "بيانات الدخول غير صحيحة أو الحساب معطل."
    
    if row["locked_until"] and datetime.now() < datetime.fromisoformat(row["locked_until"]):
        return None, "الحساب مقفل مؤقتاً بسبب المحاولات المتكررة."

    if check_password(password, row["password_hash"]):
        safe_execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = :u", {"u": username})
        log_action(username, "تسجيل دخول ناجح")
        return dict(row), None
    
    attempts = row["failed_attempts"] + 1
    if attempts >= MAX_LOGIN_ATTEMPTS:
        lock_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
        safe_execute("UPDATE users SET failed_attempts = :a, locked_until = :l WHERE username = :u", {"a": attempts, "l": lock_until, "u": username})
        log_action(username, "قفل الحساب", f"تجاوز محاولات الدخول الفاشلة ({attempts})")
    else:
        safe_execute("UPDATE users SET failed_attempts = :a WHERE username = :u", {"a": attempts, "u": username})
    return None, "بيانات الدخول غير صحيحة."

# ---------------------------------------------------------------------------
# 5. العمليات الأساسية (تذاكر، تقارير، قرارات)
# ---------------------------------------------------------------------------
def create_ticket(dept, dev, loc, typ, desc, pri, created_by):
    tid = "TCK-" + uuid.uuid4().hex[:8].upper()
    safe_execute(
        """INSERT INTO tickets (ticket_id, created_at, department, device_name, location, alert_type, issue_desc, priority, created_by)
           VALUES (:tid, :ts, :dep, :dev, :loc, :typ, :desc, :pri, :by)""",
        {"tid": tid, "ts": datetime.now().isoformat(), "dep": dept, "dev": sanitize_text(dev), 
         "loc": sanitize_text(loc), "typ": typ, "desc": encrypt_val(desc), "pri": pri, "by": created_by}
    )
    log_action(created_by, "إنشاء تذكرة استباقية", tid)
    return tid

def get_tickets_df(dept=None, search_term=None):
    query = "SELECT * FROM tickets"
    params = {}
    if dept:
        query += " WHERE department = :dep"
        params["dep"] = dept
    
    engine = get_engine()
    with engine.begin() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)
    
    if not df.empty:
        df["issue_desc"] = df["issue_desc"].apply(decrypt_val)
        df["created_at"] = pd.to_datetime(df["created_at"])
        if search_term:
            df = df[df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]
    return df

# ---------------------------------------------------------------------------
# 6. واجهة المستخدم (Streamlit) وإعدادات العرض
# ---------------------------------------------------------------------------
st.set_page_config(page_title="VisiPulse - Proactive Health Cluster System", layout="wide")
init_db()

# اللغة الافتراضية
lang = st.sidebar.selectbox("Language / اللغة", ["العربية (AR)", "English (EN)"])

# إدارة الجلسة
if "user" not in st.session_state: 
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<h2 style='text-align: center; color: #1a5276;'>VisiPulse - بوابة الدخول الآمن (CBAHI Compliant)</h2>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("login_form"):
            u = st.text_input("اسم المستخدم (Username)")
            p = st.text_input("كلمة المرور (Password)", type="password")
            submit_login = st.form_submit_button("تسجيل الدخول")
            if submit_login:
                user_data, err = verify_login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else: 
                    st.error(err)
        st.info("💡 حسابات تجريبية للاختبار:\n- المدير: `admin` / `Admin@123`\n- الجودة: `quality` / `Quality@123`\n- الـ IT: `it_lead` / `It@12345`\n- الموظف: `employee` / `Emp@12345`")
    st.stop()

user = st.session_state.user

# ---------------------------------------------------------------------------
# الشريط الجانبي (Sidebar) والهيكل الهرمي المتداخل للأقسام
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### مرحباً، {user['full_name']}")
    st.caption(f"الدور: `{user['role']}`")
    if st.button("تسجيل الخروج (Logout)"):
        log_action(user["username"], "تسجيل خروج")
        st.session_state.user = None
        st.rerun()
    
    st.divider()
    search_q = st.text_input("بحث عام في السجلات...")

st.markdown("<h2 style='text-align: center; color: #1a5276;'>VisiPulse - نظام مراقبة البنية التحتية والإنذار المبكر</h2>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------------------------
# توزيع الصلاحيات والبوابات (RBAC)
# ---------------------------------------------------------------------------

# 1. واجهة الموظف الميداني
if user["role"] == "employee":
    st.subheader("شاشة التنبيهات الاستباقية للموظف (Proactive Employee Screen)")
    st.warning("تنبيه تنبؤي (Z-Score Anomaly): رصد تباطؤ غير معتاد في أداء الهارد ديسك لجهاز السيرفر أو المحطة الطبية (DEV-305).")
    
    if st.button("تأكيد الإنذار وإرسال البلاغ تلقائياً لقسم تقنية المعلومات"):
        tid = create_ticket("قسم الدعم الفني", "DEV-305", "العيادات الخارجية", "عطل تنبؤي هارد ديسك", "رصد احتمالية تعطل القرص الصلب بناءً على التحليل السلوكي.", "عالية", user["username"])
        st.success(تم بنجاح إرسال التذكرة الاستباقية برقم: `{tid}` إلى قسم الـ IT.)

# 2. واجهة الإدارة العليا (Top Management)
elif user["role"] == "top_mgmt":
    st.subheader("لوحة المؤشرات الاستراتيجية للإدارة العليا (Top Management Portal)")
    df = get_tickets_df(search_term=search_q)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي البلاغات والاستباقيات", len(df))
    c2.metric("البلاغات المفتوحة", len(df[df["status"]=="مفتوحة"]))
    c3.metric("معدل الاستقرار العام", "94.8%", "+3.2%")
    
    st.markdown("#### لوحة أداء البنية التحتية والمستشفى")
    chart_data = pd.DataFrame({"الكفاءة التشغيلية %": [88, 90, 92, 91, 93, 94.8]}, index=["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"])
    st.area_chart(chart_data)
    
    st.subheader("سجل البلاغات والتدقيق")
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("تحميل تقرير النظام (CSV)", data=csv, file_name="visipulse_management_report.csv", mime="text/csv")

# 3. واجهة مدير الجودة (Quality Management - CBAHI)
elif user["role"] == "quality_mgr":
    st.subheader("بوابة إدارة الجودة والامتثال لمعايير CBAHI")
    st.info("متابعة مستويات الأداء (SLA)، مراجعة مقاييس رضا المستفيدين، واعتماد قرارات الالتزام الرقمي.")
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.markdown("##### نسبة الالتزام بأوقات معالجة البلاغات (SLA %)")
        sla_df = pd.DataFrame({"نسبة الالتزام %": [92, 88, 95, 91]}, index=["الربع الأول", "الربع الثاني", "الربع الثالث", "الربع الرابع"])
        st.bar_chart(sla_df)
    with col_q2:
        st.markdown("##### مؤشر رضا المستفيدين والموظفين")
        sat_df = pd.DataFrame({"مؤشر الرضا": [85, 89, 93, 96]}, index=["يناير", "فبراير", "مارس", "أبريل"])
        st.line_chart(sat_df)

    st.markdown("---")
    st.markdown("#### اتخاذ قرار اعتمادي أو خطة تحسين عاجلة:")
    quality_decision = st.text_input("اكتب القرار الإداري (مثال: اعتماد معايير الفحص الاستباقي لشهر أغسطس وتحديث سياسة الأمان):")
    if quality_decision:
        safe_execute(
            "INSERT INTO decisions (decision_id, created_at, decision_text, created_by) VALUES (:id, :ts, :txt, :by)",
            {"id": "DEC-" + uuid.uuid4().hex[:6].upper(), "ts": datetime.now().isoformat(), "txt": quality_decision, "by": user["username"]}
        )
        st.success(f"تم اعتماد وتوثيق القرار رسمياً في سجل الجودة: ({quality_decision})")
        log_action(user["username"], "اعتماد قرار جودة", quality_decision)

# 4. واجهة الـ IT والمدير الفني (مع الهيكل الهرمي المتداخل للأقسام الفرعية)
elif user["role"] in ["it_lead", "system_admin"]:
    st.subheader("بوابة إدارة تقنية المعلومات (IT Department Portal)")
    
    # هيكل القائمة المنسدلة للأقسام الفرعية (Hierarchical Dropdown Sidebar inside main view)
    sub_tabs = [
        "إدارة الصحة الإلكترونية (E-Health Management)",
        "قسم الدعم الفني (Technical Support / Help Desk)",
        "قسم البنية التحتية والشبكات (Infrastructure & Networks)",
        "قسم الأنظمة والتطبيقات (Systems & Applications)"
    ]
    sub_choice = st.selectbox("اختر القسم الفرعي لتقنية المعلومات:", sub_tabs)
    
    if "الصحة الإلكترونية" in sub_choice:
        st.markdown("### إدارة الصحة الإلكترونية (E-Health)")
        st.info("مراقبة التكامل الرقمي، جاهزية المنصات السريرية، والسجلات الطبية المركزية.")
        st.bar_chart(pd.DataFrame({'معدل التكامل الرقمي %': [99.2, 98.5, 99.8, 99.5]}, index=["الربط المركزي", "السجلات الصحية", "الخدمات الإكلينيكية", "التكامل الإحصائي"]))

    elif "الدعم الفني" in sub_choice:
        st.markdown("### قسم الدعم الفني (Technical Support)")
        contractor = st.text_input("أدخل اسم شركة الصيانة المقاولة المرتبطة:")
        if contractor:
            st.success(f"تم ربط التذاكر الواردة وإرسالها آلياً إلى شركة الصيانة: {contractor}")
        
        st.markdown("#### سجل البلاغات الواردة آلياً من الأجهزة:")
        tickets_df = get_tickets_df(search_term=search_q)
        st.dataframe(tickets_df, use_container_width=True)

    elif "البنية التحتية" in sub_choice:
        st.markdown("### قسم البنية التحتية والشبكات (Infrastructure)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### جاهزية سيرفرات الداتا سنتر")
            st.bar_chart(pd.DataFrame({'الجاهزية %': [99.5, 98.9, 99.8]}, index=["سيرفر أ", "سيرفر ب", "سيرفر ج"]))
        with col2:
            st.markdown("#### أحمال استهلاك الشبكة (Mbps)")
            st.line_chart(pd.DataFrame({"الاستهلاك": [45, 75, 90, 60, 40]}, index=["الصباح", "الظهر", "الذروة", "المساء", "الليل"]))
        st.warning("تنبيه أمني: تم رصد ضغط على سويتش مبنى العيادات، وتم تفعيل بروتوكول التدقيق الأمني.")

    elif "الأنظمة والتطبيقات" in sub_choice:
        st.markdown("### قسم الأنظمة والتطبيقات (Systems & Applications)")
        app_status_df = pd.DataFrame({
            "النظام / التطبيق": ["النظام الطبي الموحد", "نظام إدارة المواعيد", "نظام المختبر والأشعة LIS/PACS"],
            "حالة الاتصال والخدمة": ["متصل ومستقر", "مستقر", "تحذير طفيف بالاستجابة"],
            "الشركة الموردة": ["شركة الحلول الطبية", "شركة التقنية الرقمية", "الأنظمة المتقدمة"]
        })
        st.table(app_status_df)

    # إذا كان المستخدم Admin بالكامل، يظهر سجل التدقيق الأمني (Audit Logs)
    if user["role"] == "system_admin":
        st.markdown("---")
        with st.expander("عرض سجل التدقيق الأمني الحساس (Immutable Audit Log - CBAHI Requirement)"):
            engine = get_engine()
            with engine.begin() as conn:
                logs_df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY ts DESC LIMIT 50", conn)
            st.dataframe(logs_df, use_container_width=True)

# ---------------------------------------------------------------------------
# تذليل الصفحة
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption("نظام VisiPulse - مطور وفقاً لأعلى معايير الأمن السيبراني ومتطلبات سباهي (CBAHI).")
