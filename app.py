import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# تهيئة الذاكرة المشتركة للتذاكر والتنبيهات
if "tickets" not in st.session_state:
    st.session_state.tickets = []

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
    st.error("تنبيه استباقي: تم رصد تعطل في نقطة الاتصال أو خلل في الحاسب الآلي في قسمك.")
    
    with st.form("proactive_alert_form"):
        # حقل القسم كتابة حرة لتغطية كافة الأقسام
        dept = st.text_input("اسم القسم (اكتب القسم التابع له):")
        device = st.text_input("رقم الجهاز:")
        issue_type = st.selectbox("نوع المشكلة المكتشفة:", ["تعطل شبكة", "رصد فيروس", "عطل هاردوير (PC)"])
        
        is_hardware = (issue_type == "عطل هاردوير (PC)")
        maint_needed = "غير مطلوب"
        if is_hardware:
            maint_needed = st.radio("هل يحتاج لصيانة فورية؟", ["نعم", "لا"])
            
        submitted = st.form_submit_button("OK - إرسال التنبيه لقسم الدعم الفني")
        
        if submitted:
            if dept.strip() == "":
                st.warning("يرجى كتابة اسم القسم قبل الإرسال.")
            else:
                new_ticket = {
                    "القسم": dept,
                    "الجهاز": device,
                    "المشكلة": issue_type,
                    "نوع العطل": "هاردوير" if is_hardware else "شبكة/برمجيات",
                    "يحتاج صيانة": maint_needed,
                    "الحالة": "مفتوحة وعاجلة"
                }
                st.session_state.tickets.append(new_ticket)
                st.success("تم تأكيد التنبيه وإرساله لقسم الدعم الفني بنجاح.")

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
            # عرض التذاكر
            df = pd.DataFrame(st.session_state.tickets)
            st.table(df)
            
            # زر المسح
            if st.button("مسح جميع البلاغات المعالجة"):
                st.session_state.tickets = []
                st.rerun()
            
            # زر تصدير CSV
            csv_data = generate_stats_csv()
            if csv_data:
                st.download_button("استخراج تقرير CSV", data=csv_data, file_name="Proactive_Tickets.csv", mime="text/csv")
        else:
            st.info("لا توجد بلاغات استباقية حالياً.")
    elif it_pass:
        st.warning("كود الدعم الفني غير صحيح.")
