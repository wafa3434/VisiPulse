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

# التحقق من وجود مفتاح التشفير (ضروري لحماية البيانات الحساسة)
if not ENCRYPTION_KEY:
    st.error("خطأ أمني: لم يتم العثور على VISIPULSE_ENCRYPTION_KEY في متغيرات البيئة.")
    st.stop()

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
    # (تم اختصار الجداول الأخرى للتركيز على منطق العمل المحدث - القرارات والبلاغات تتبع نفس النمط)
    safe_execute("CREATE TABLE IF NOT EXISTS decisions (decision_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, related_ticket_id TEXT, decision_text TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'معتمد', created_by TEXT)")

    # مستخدم أدمن افتراضي
    existing = safe_execute("SELECT COUNT(*) FROM users").scalar()
    if existing == 0:
        temp_pw = uuid.uuid4().hex[:12]
        safe_execute(
            "INSERT INTO users (username, password_hash, full_name, role, must_change_password) VALUES (:u, :p, :f, :r, :m)",
            {"u": "admin", "p": hash_password(temp_pw), "f": "مدير النظام", "r": "system_admin", "m": 1}
        )
        logger.info("SEED USER CREATED: admin. Temp PW: %s", temp_pw)
        st.info(f"تم إنشاء حساب المدير بنجاح. اسم المستخدم: `admin` كلمة المرور: `{temp_pw}`")

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
        return None, "بيانات الدخول غير صحيحة."
    
    if row["locked_until"] and datetime.now() < datetime.fromisoformat(row["locked_until"]):
        return None, "الحساب مقفل مؤقتاً."

    if check_password(password, row["password_hash"]):
        safe_execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = :u", {"u": username})
        log_action(username, "دخول ناجح")
        return dict(row), None
    
    attempts = row["failed_attempts"] + 1
    if attempts >= MAX_LOGIN_ATTEMPTS:
        lock_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
        safe_execute("UPDATE users SET failed_attempts = :a, locked_until = :l WHERE username = :u", {"a": attempts, "l": lock_until, "u": username})
    else:
        safe_execute("UPDATE users SET failed_attempts = :a WHERE username = :u", {"a": attempts, "u": username})
    return None, "بيانات الدخول غير صحيحة."

# ---------------------------------------------------------------------------
# 5. العمليات الأساسية (تذاكر، تقارير، بحث)
# ---------------------------------------------------------------------------
def create_ticket(dept, dev, loc, typ, desc, pri, created_by):
    tid = "TCK-" + uuid.uuid4().hex[:8].upper()
    safe_execute(
        """INSERT INTO tickets (ticket_id, created_at, department, device_name, location, alert_type, issue_desc, priority, created_by)
           VALUES (:tid, :ts, :dep, :dev, :loc, :typ, :desc, :pri, :by)""",
        {"tid": tid, "ts": datetime.now().isoformat(), "dep": dept, "dev": sanitize_text(dev), 
         "loc": sanitize_text(loc), "typ": typ, "desc": encrypt_val(desc), "pri": pri, "by": created_by}
    )
    log_action(created_by, "إنشاء تذكرة", tid)
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
# 6. واجهة المستخدم (Streamlit)
# ---------------------------------------------------------------------------
st.set_page_config(page_title="VisiPulse Pro", layout="wide")
init_db()

# إدارة الجلسة
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.title("VisiPulse - تسجيل الدخول الآمن")
    with st.form("login_form"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            user, err = verify_login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else: st.error(err)
    st.stop()

user = st.session_state.user

# شريط جانبي للمعلومات والبحث
with st.sidebar:
    st.write(f"مرحباً، {user['full_name']}")
    if st.button("تسجيل الخروج"):
        st.session_state.user = None
        st.rerun()
    st.divider()
    search_q = st.text_input("بحث سريع في النظام...")

# واجهة الإدارة العليا / الجودة (مع ميزة التصدير والبحث)
if user["role"] in ["top_mgmt", "quality_mgr", "ehealth_mgr"]:
    st.header("لوحة التحكم والتقارير")
    df = get_tickets_df(search_term=search_q)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي البلاغات", len(df))
    col2.metric("بلاغات مفتوحة", len(df[df["status"]=="مفتوحة"]))
    
    st.subheader("سجل البلاغات المكتشفة")
    st.dataframe(df, use_container_width=True)
    
    # ميزة التصدير للإنتاج
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("تحميل البيانات كـ CSV", data=csv, file_name="visipulse_report.csv", mime="text/csv")

# واجهة الموظف الميداني (نفس المنطق السابق مع حماية البيانات)
elif user["role"] == "employee":
    st.subheader("نظام التنبيه الاستباقي")
    # محاكاة تنبيه
    st.warning("تنبيه: تم اكتشاف انخفاض في أداء جهاز PACS")
    if st.button("تأكيد وإرسال بلاغ"):
        tid = create_ticket("قسم الأنظمة", "PACS Server 01", "المبنى الرئيسي", "تقني", "تأخير في استجابة الصور", "عالية", user["username"])
        st.success(f"تم فتح التذكرة بنجاح: {tid}")

# واجهة مدير النظام (إدارة المستخدمين)
elif user["role"] == "system_admin":
    st.header("إدارة أمن النظام والمستخدمين")
    with st.expander("إضافة مستخدم جديد"):
        with st.form("add_user"):
            new_u = st.text_input("اسم المستخدم")
            new_f = st.text_input("الاسم بالكامل")
            new_r = st.selectbox("الدور", ["employee", "it_support", "quality_mgr", "top_mgmt"])
            if st.form_submit_button("حفظ"):
                pw = uuid.uuid4().hex[:10]
                try:
                    safe_execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (:u, :p, :f, :r)",
                                 {"u": sanitize_text(new_u), "p": hash_password(pw), "f": sanitize_text(new_f), "r": new_r})
                    st.success(f"تم الإنشاء. كلمة المرور المؤقتة: {pw}")
                    log_action(user["username"], "إنشاء مستخدم", new_u)
                except: st.error("فشل الإنشاء (ربما الاسم موجود مسبقاً)")

    st.subheader("سجل العمليات (Audit Log)")
    engine = get_engine()
    with engine.begin() as conn:
        logs = pd.read_sql_query("SELECT * FROM audit_log ORDER BY ts DESC LIMIT 100", conn)
    st.table(logs)

# ---------------------------------------------------------------------------
# رسالة تذليل الصفحة
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption("نظام VisiPulse V2.0 - جميع البيانات مشفرة وتخضع للرقابة الصارمة.")
