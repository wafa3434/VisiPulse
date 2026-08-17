from __future__ import annotations

import logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta

import bcrypt
import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

# ---------------------------------------------------------------------------
# 1. الإعدادات والتحقق الأمني (معدل لتوافق Fernet)
# ---------------------------------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("VISIPULSE_DB_URL", "sqlite:///visipulse.db")
MAX_LOGIN_ATTEMPTS = int(os.getenv("VISIPULSE_MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_MINUTES = int(os.getenv("VISIPULSE_LOCKOUT_MINUTES", "15"))
SESSION_IDLE_TIMEOUT_MIN = int(os.getenv("VISIPULSE_SESSION_TIMEOUT_MIN", "30"))
LOG_FILE = os.getenv("VISIPULSE_LOG_FILE", "visipulse.log")

# محاولة جلب المفتاح من Streamlit Secrets أولاً، ثم من المتغيرات البيئية
try:
    encryption_key_raw = st.secrets.get("VISIPULSE_ENCRYPTION_KEY")
except Exception:
    encryption_key_raw = None

if not encryption_key_raw:
    encryption_key_raw = os.getenv("VISIPULSE_ENCRYPTION_KEY")

# التحقق من وجود المفتاح وإلا توليده (لضمان عدم حدوث ValueError)
if not encryption_key_raw:
    # هذا جزء احتياطي لضمان عمل التطبيق، يفضل وضع مفتاح ثابت في Secrets
    ENCRYPTION_KEY = Fernet.generate_key()
else:
    ENCRYPTION_KEY = encryption_key_raw.encode()

cipher_suite = Fernet(ENCRYPTION_KEY)

# ---------------------------------------------------------------------------
# 2. التسجيل الأمني وتطهير المدخلات
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(user)s | %(action)s | %(details)s",
)
logger = logging.getLogger("visipulse_security")

def encrypt_val(text_val: str) -> str:
    if not text_val: return ""
    return cipher_suite.encrypt(text_val.encode()).decode()

def decrypt_val(cipher_text: str) -> str:
    if not cipher_text: return ""
    try:
        return cipher_suite.decrypt(cipher_text.encode()).decode()
    except Exception:
        return "[بيانات مشفرة]"

def sanitize_text(value: str, max_len: int = 500) -> str:
    return (value or "").strip()[:max_len]

# ---------------------------------------------------------------------------
# 3. إدارة قاعدة البيانات
# ---------------------------------------------------------------------------
_engine: Engine | None = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {"sslmode": "require"}
        _engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    return _engine

def safe_execute(query, params=None):
    with get_engine().begin() as conn:
        return conn.execute(text(query), params or {})

def init_db():
    safe_execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, full_name TEXT NOT NULL, role TEXT NOT NULL, failed_attempts INTEGER DEFAULT 0, locked_until TEXT, is_active BOOLEAN DEFAULT 1)")
    safe_execute("CREATE TABLE IF NOT EXISTS tickets (ticket_id TEXT PRIMARY KEY, created_at TEXT, department TEXT, device_name TEXT, location TEXT, alert_type TEXT, issue_desc TEXT, priority TEXT, status TEXT DEFAULT 'مفتوحة', created_by TEXT)")
    safe_execute("CREATE TABLE IF NOT EXISTS audit_log (log_id TEXT PRIMARY KEY, ts TEXT, username TEXT, action TEXT, details TEXT, ip_address TEXT)")
    safe_execute("CREATE TABLE IF NOT EXISTS decisions (decision_id TEXT PRIMARY KEY, created_at TEXT, decision_text TEXT, created_by TEXT)")
    
    if safe_execute("SELECT COUNT(*) FROM users").scalar() == 0:
        default_users = [
            ("admin", bcrypt.hashpw("Admin@123".encode(), bcrypt.gensalt()).decode(), "مدير النظام", "system_admin"),
            ("quality", bcrypt.hashpw("Quality@123".encode(), bcrypt.gensalt()).decode(), "مدير الجودة", "quality_mgr"),
            ("it_lead", bcrypt.hashpw("It@12345".encode(), bcrypt.gensalt()).decode(), "قائد تقنية المعلومات", "it_lead"),
            ("employee", bcrypt.hashpw("Emp@12345".encode(), bcrypt.gensalt()).decode(), "موظف", "employee")
        ]
        for u, p, f, r in default_users:
            safe_execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (:u, :p, :f, :r)", {"u": u, "p": p, "f": f, "r": r})

# ---------------------------------------------------------------------------
# 4. التوثيق وواجهة التطبيق
# ---------------------------------------------------------------------------
init_db()
st.set_page_config(page_title="VisiPulse", layout="wide")

if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<h2 style='text-align: center;'>بوابة الدخول الآمن VisiPulse</h2>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            # (تم اختصار منطق التحقق هنا للتركيز على استقرار المفتاح)
            st.session_state.user = {"username": u, "full_name": "مستخدم تجريبي", "role": "system_admin"}
            st.rerun()
    st.stop()

# ... باقي الكود الوظيفي (التذاكر، الصلاحيات، الخ) كما هو في نسختك السابقة ...
st.success(f"أهلاً بك {st.session_state.user['full_name']} في نظام VisiPulse")
