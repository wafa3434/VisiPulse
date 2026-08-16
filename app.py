import streamlit as st
import pandas as pd
import random

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# دالة لجلب معلومات الجهاز والقسم والعطل المرصود تلقائياً
def get_proactive_alert():
    # محاكاة لعطل يتم رصده استباقياً بواسطة النظام
    issues_list = ["تعطل شبكة الاتصال", "رصد برمجية خبيثة (فيروس)", "عطل هاردوير في اللوحة الأم (PC)"]
    return {
        "device_name": "Desktop-2345-ICU",
        "department": "العناية المركزة (ICU)",
        "detected_issue": random.choice(issues_list)
    }

# تهيئة الذاكرة المشتركة للتذاكر والتنبيهات
if "tickets" not in st.session_state:
    st.session_state.tickets = []

if "current_alert" not in st.session_state:
    st.session_state.current_alert = get_proactive_alert()

# --- وظيفة تصدير البيانات ---
def generate_stats_csv():
    if not st.session_state.tickets:
        return ""
    df = pd.DataFrame(st.session_state.tickets)
    return df.to_csv(index=False).encode('utf-8-sig')

# --- الترويسة الرئيسية ---
st.markdown("<h2 style='text-align: center; color: #1a5276;'>VisiPulse - نظام مراقبة البنية التحتية والإنذار المبكر</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- التبويبات الرئيسية ---
tab1, tab2, tab3 = st.tabs(["شاشة الموظفين (الاستباقية)", "بوابة الإدارة العليا", "بوابة تقنية المعلومات (IT)"])

# 1. شاشة الموظفين (الاستباقية)
with tab1:
    st.subheader("لوحة التنبيهات الاستباقية للموظف")
    
    alert = st.session_state.current_alert
    
    # ظهور العطل استباقياً بشكل مباشر في رسالة التنبيه
    st.error(f"تنبيه استباقي: تم رصد مشكلة ({alert['detected_issue']}) في جهازك الحالي بشكل تلقائي.")
    
    with st.form("proactive_alert_form"):
        st.write("اسم القسم المرصود تلقائياً:", alert["department"])
        st.write("معرف الجهاز المرصود تلقائياً:", alert["device_name"])
        st.write("نوع المشكلة المرصودة تلقائياً:", alert["detected_issue"])
        
        is_hardware = ("هاردوير" in alert["detected_issue"])
        maint_needed = "غير مطلوب"
        if is_hardware:
            maint_needed = st.radio("هل يحتاج لصيانة فورية؟", ["نعم", "لا"])
            
        submitted = st.form_submit_button("OK - تأكيد وإرسال التنبيه لقسم الدعم الفني")
        
        if submitted:
            new_ticket = {
                "القسم": alert["department"],
                "معرف الجهاز": alert["device_name"],
                "المشكلة": alert["detected_issue"],
                "نوع العطل": "هاردوير" if is_hardware else "شبكة/برمجيات",
                "يحتاج صيانة": maint_needed,
                "شركة الصيانة": "قيد المعالجة",
                "تفاصيل صيانة المقاول": "قيد المعالجة",
                "الحالة": "مفتوحة وعاجلة"
            }
            st.session_state.tickets.append(new_ticket)
            st.success("تم تأكيد التنبيه وإرساله لقسم الدعم الفني بنجاح.")
            # توليد عطل جديد للتجربة في المرات القادمة
            st.session_state.current_alert = get_proactive_alert()

# 2. بوابة الإدارة العليا
with tab2:
    mgmt_pass = st.text_input("أدخل كود الإدارة:", type="password", key="mgmt_login")
    if mgmt_pass == "mgmt999":
        st.subheader("لوحة المؤشرات الاستراتيجية وأداء المستشفى")
        c1, c2, c3 = st.columns(3)
        c1.metric("الأعطال التي تم تلافيها", "28 عطل", "+5")
        c2.metric("نسبة الاستقرار العام", "94.8%", "+3.2%")
        c3.metric("التوفير المالي", "150 ألف ر.س", "+12%")
    elif mgmt_pass:
        st.warning("كود الإدارة غير صحيح.")

# 3. بوابة تقنية المعلومات (IT)
with tab3:
    it_pass = st.text_input("أدخل كود الدعم الفني:", type="password", key="it_login")
    if it_pass == "it123":
        st.subheader("إدارة البلاغات الاستباقية")
        
        if st.session_state.tickets:
            df = pd.DataFrame(st.session_state.tickets)
            st.table(df)
            
            st.markdown("---")
            st.subheader("إغلاق وتحديث البلاغ (إدخال بيانات شركة المقاولات)")
            
            with st.form("close_ticket_form"):
                ticket_index = st.selectbox("اختر رقم البلاغ المراد إغلاقه/تحديثه:", options=range(len(st.session_state.tickets)))
                contractor_name = st.text_input("اسم شركة المقاولات الصيانة (كتابة):")
                maintenance_details = st.text_input("تفاصيل عطل الصيانة (كتابة):")
                
                close_submitted = st.form_submit_button("إغلاق البلاغ وتحديث السجل")
                
                if close_submitted:
                    st.session_state.tickets[ticket_index]["شركة الصيانة"] = contractor_name if contractor_name else "لا توجد"
                    st.session_state.tickets[ticket_index]["تفاصيل صيانة المقاول"] = maintenance_details if maintenance_details else "لا توجد"
                    st.session_state.tickets[ticket_index]["الحالة"] = "مغلقة ومعالجة"
                    st.success("تم تحديث وإغلاق البلاغ بنجاح.")
                    st.rerun()
            
            if st.button("مسح جميع البلاغات المعالجة"):
                st.session_state.tickets = []
                st.rerun()
            
            csv_data = generate_stats_csv()
            if csv_data:
                st.download_button("استخراج تقرير CSV", data=csv_data, file_name="Proactive_Tickets.csv", mime="text/csv")
        else:
            st.info("لا توجد بلاغات استباقية حالياً.")
    elif it_pass:
        st.warning("كود الدعم الفني غير صحيح.")
