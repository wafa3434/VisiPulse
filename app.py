import streamlit as st
import pandas as pd
import random

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - E-Health Management System", layout="wide")

# تهيئة الذاكرة للتذاكر
if "tickets" not in st.session_state:
    st.session_state.tickets = []

# دالة توليد تنبيهات استباقية لكل قسم
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
        "device_name": f"THC-{random.randint(100,999)}-SYS"
    }

if "current_alert" not in st.session_state:
    st.session_state.current_alert = get_proactive_alert()

# وظيفة تصدير التقارير
def generate_stats_csv():
    if not st.session_state.tickets:
        return ""
    df = pd.DataFrame(st.session_state.tickets)
    return df.to_csv(index=False).encode('utf-8-sig')

# الترويسة
st.markdown("<h2 style='text-align: center; color: #1a5276;'>VisiPulse - إدارة الصحة الإلكترونية</h2>", unsafe_allow_html=True)
st.markdown("---")

# التبويبات
tab1, tab2, tab3 = st.tabs(["شاشة الموظفين (استباقية)", "بوابة الإدارة العليا", "بوابة الأقسام (IT & Quality)"])

# 1. شاشة الموظفين
with tab1:
    st.subheader("لوحة التنبيهات الاستباقية")
    alert = st.session_state.current_alert
    
    # العطل يظهر استباقياً فوراً
    st.error(f"تنبيه استباقي مرصود في {alert['department']}: {alert['detected_issue']}")
    
    with st.form("proactive_alert_form"):
        st.write("القسم:", alert["department"])
        st.write("المعرف:", alert["device_name"])
        st.write("المشكلة:", alert["detected_issue"])
        
        is_hardware = ("البنية التحتية" in alert["department"] or "الدعم الفني" in alert["department"])
        maint_needed = "غير مطلوب"
        if is_hardware:
            maint_needed = st.radio("هل يحتاج لصيانة خارجية فورية؟", ["نعم", "لا"])
            
        submitted = st.form_submit_button("تأكيد البلاغ وإرساله")
        
        if submitted:
            new_ticket = {
                "القسم": alert["department"],
                "المعرف": alert["device_name"],
                "المشكلة": alert["detected_issue"],
                "صيانة مقاول": maint_needed,
                "شركة الصيانة": "قيد المعالجة",
                "تفاصيل الصيانة": "قيد المعالجة",
                "الحالة": "مفتوحة وعاجلة"
            }
            st.session_state.tickets.append(new_ticket)
            st.success("تم إرسال البلاغ بنجاح.")
            st.session_state.current_alert = get_proactive_alert()

# 2. الإدارة العليا
with tab2:
    mgmt_pass = st.text_input("كود الإدارة:", type="password", key="mgmt_login")
    if mgmt_pass == "mgmt999":
        c1, c2, c3 = st.columns(3)
        c1.metric("البلاغات الاستباقية", len(st.session_state.tickets), "+")
        c2.metric("مستوى الاستقرار", "96%", "+")
        c3.metric("جودة الخدمات", "98%", "+")

# 3. الأقسام (IT & Quality)
with tab3:
    it_pass = st.text_input("كود الدعم الفني:", type="password", key="it_login")
    if it_pass == "it123":
        if st.session_state.tickets:
            df = pd.DataFrame(st.session_state.tickets)
            st.table(df)
            
            st.subheader("تحديث وإغلاق البلاغ")
            with st.form("close_ticket_form"):
                ticket_index = st.selectbox("اختر البلاغ للتحديث:", options=range(len(st.session_state.tickets)))
                contractor_name = st.text_input("اسم شركة مقاولات الصيانة (كتابة):")
                maintenance_details = st.text_input("تفاصيل تقرير الصيانة/الجودة (كتابة):")
                
                if st.form_submit_button("إغلاق البلاغ وتوثيقه"):
                    st.session_state.tickets[ticket_index]["شركة الصيانة"] = contractor_name
                    st.session_state.tickets[ticket_index]["تفاصيل الصيانة"] = maintenance_details
                    st.session_state.tickets[ticket_index]["الحالة"] = "مغلقة ومعتمدة"
                    st.rerun()
            
            if st.download_button("تصدير التقرير", data=generate_stats_csv(), file_name="Report.csv"):
                pass
