import streamlit as st
import pandas as pd
import random

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - E-Health Proactive Monitoring System", layout="wide")

# تهيئة الذاكرة للتذاكر
if "tickets" not in st.session_state:
    st.session_state.tickets = []

# دالة توليد تنبيهات استباقية
def get_proactive_alert():
    departments_data = [
        {"dept": "قسم الأنظمة والتطبيقات", "issue": "تعطل مفاجئ في النظام الطبي/قواعد البيانات"},
        {"dept": "قسم الدعم الفني", "issue": "تراكم بلاغات الهاردوير أو بطء استجابة الأجهزة"},
        {"dept": "قسم البنية التحتية", "issue": "انقطاع أو تلف نقطة الاتصال (Access Point)"},
        {"dept": "قسم الجودة", "issue": "رصد فجوات في مؤشرات الأداء التقني ومعايير الاعتماد"}
    ]
    selected = random.choice(departments_data)
    return {
        "department": selected["dept"],
        "detected_issue": selected["issue"],
        "device_name": f"THC-MONITOR-{random.randint(100,999)}"
    }

if "current_alert" not in st.session_state:
    st.session_state.current_alert = get_proactive_alert()

# وظيفة تصدير التقارير
def generate_stats_csv():
    if not st.session_state.tickets:
        return ""
    df = pd.DataFrame(st.session_state.tickets)
    return df.to_csv(index=False).encode('utf-8-sig')

# --- الهيدر والشعار ---
header_col1, header_col2, header_col3 = st.columns([1, 6, 2])
with header_col1:
    try:
        st.image("logo.jpeg", width=120)
    except:
        st.write("الشعار")
with header_col2:
    st.markdown("<h3 style='text-align: center; color: #1a5276;'>VisiPulse - نظام المراقبة الاستباقية لإدارة الصحة الإلكترونية</h3>", unsafe_allow_html=True)
with header_col3:
    lang = st.selectbox("Language / اللغة", ["العربية", "English"])

st.markdown("---")

# التبويبات الرئيسية
tab1, tab2, tab3 = st.tabs(["شاشة الموظفين (المراقبة الاستباقية)", "بوابة الإدارة العليا", "بوابة الأقسام (IT & Quality)"])

# 1. شاشة الموظفين
with tab1:
    st.subheader("لوحة التنبيهات الاستباقية الفورية")
    alert = st.session_state.current_alert
    st.error(f"تنبيه استباقي من نظام المراقبة في {alert['department']}: {alert['detected_issue']}")
    
    with st.form("proactive_alert_form"):
        st.write("القسم:", alert["department"])
        st.write("المعرف:", alert["device_name"])
        st.write("المشكلة:", alert["detected_issue"])
        if st.form_submit_button("تأكيد البلاغ وإرساله"):
            new_ticket = {
                "القسم": alert["department"],
                "المعرف": alert["device_name"],
                "المشكلة": alert["detected_issue"],
                "الحالة": "مفتوحة وعاجلة"
            }
            st.session_state.tickets.append(new_ticket)
            st.success("تم إرسال البلاغ بنجاح.")
            st.session_state.current_alert = get_proactive_alert()

# 2. الإدارة العليا
with tab2:
    mgmt_pass = st.text_input("كود الإدارة العليا:", type="password", key="mgmt_login")
    if mgmt_pass == "mgmt999":
        st.subheader("مؤشرات الأداء الاستراتيجية")
        c1, c2, c3 = st.columns(3)
        c1.metric("الأعطال المتلافة", len(st.session_state.tickets) + 12, "+4")
        c2.metric("الاستقرار العام", "97.4%", "+1.2%")
        c3.metric("جودة الخدمات", "99.1%", "+0.8%")
    elif mgmt_pass:
        st.warning("كود الإدارة غير صحيح.")

# 3. الأقسام (IT & Quality) - الأرقام انتقلت هنا
with tab3:
    it_pass = st.text_input("أدخل كود الدعم الفني وإدارة الأقسام:", type="password", key="it_login")
    if it_pass == "it123":
        st.subheader("لوحة تحكم نظام المراقبة (IT & Quality)")
        
        # الأرقام والمؤشرات الآن تظهر هنا فقط
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("حالة النظام", "متصل", "Live")
        m2.metric("الأجهزة المراقبة", "1,420", "نشط")
        m3.metric("الأنظمة المرصودة", "48", "100%")
        m4.metric("البلاغات العاجلة", len(st.session_state.tickets), "عاجل")
        
        st.markdown("---")
        
        if st.session_state.tickets:
            df = pd.DataFrame(st.session_state.tickets)
            st.table(df)
            # إمكانية إغلاق البلاغات
            if st.button("إغلاق وتصفير البلاغات المعالجة"):
                st.session_state.tickets = []
                st.rerun()
        else:
            st.info("لا توجد بلاغات استباقية نشطة.")
    elif it_pass:
        st.warning("كود الدخول غير صحيح.")
