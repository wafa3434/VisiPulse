import streamlit as st
import pandas as pd

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(
    page_title="VisiPulse - Health Cluster Proactive System",
    layout="wide"
)

# --- الترويسة العليا مع عرض الشعار وترجمة اللغات ---
header_col1, header_col2, header_col3 = st.columns([1.5, 3.5, 1])

with header_col1:
    sub_col_logo, sub_col_text = st.columns([1, 2])
    with sub_col_logo:
        try:
            st.image("logo.jpeg", width=65)
        except:
            st.write("VisiPulse")
    with sub_col_text:
        st.markdown("### **VisiPulse**")
        st.caption("طبقة الذكاء الاستباقي" if "lang" not in locals() or lang == "العربية (AR)" else "Proactive Intelligence Layer")

with header_col2:
    pass

with header_col3:
    lang = st.selectbox("Language / اللغة", ["العربية (AR)", "English (EN)"])

st.markdown("---")

# تفعيل الترجمة لعنوان النظام الرئيسي
if lang == "العربية (AR)":
    header_col2.markdown("<h2 style='text-align: center; color: #1a5276;'>نظام مراقبة البنية التحتية والإنذار المبكر</h2>", unsafe_allow_html=True)
    tab1_title = "شاشة الموظفين والتنبيهات"
    tab2_title = "بوابة الدخول الخاصة (IT & الإدارة العليا)"
else:
    header_col2.markdown("<h2 style='text-align: center; color: #1a5276;'>Infrastructure Monitoring & Early Warning System</h2>", unsafe_allow_html=True)
    tab1_title = "Employee Screen & Alerts"
    tab2_title = "Secure Login Portal (IT & Upper Management)"

# تبويبات النظام الرئيسية
tab1, tab2 = st.tabs([tab1_title, tab2_title])

with tab1:
    if lang == "العربية (AR)":
        st.subheader("شاشة التنبيهات الاستباقية للموظف")
        st.warning("تنبيه استباقي (VisiPulse): تم رصد مؤشرات تراجع في أداء الجهاز المادي (DEV-101).")
        if st.button("ضغط (OK) لتأكيد القراءة"):
            st.success("تم تأكيد الاستلام بنجاح.")
    else:
        st.subheader("Employee Proactive Alert Screen")
        st.warning("Proactive Alert (VisiPulse): Performance degradation detected in hardware device (DEV-101).")
        if st.button("Click (OK) to Confirm Reading"):
            st.success("Acknowledgment confirmed successfully.")

with tab2:
    if lang == "العربية (AR)":
        st.subheader("بوابات الدخول الآمنة للأقسام والإدارة")
        portal_choice = st.radio("اختر البوابة المطلوبة:", ["قسم تقنية المعلومات (IT Sub-divisions)", "الإدارة العليا (Upper Management)"])
        
        if portal_choice == "قسم تقنية المعلومات (IT Sub-divisions)":
            it_passcode = st.text_input("أدخل الكود السري:", type="password")
            if it_passcode == "it123":
                st.success("تم التحقق بنجاح.")
                # (باقي كود الـ IT كما هو...)
        
        elif portal_choice == "الإدارة العليا (Upper Management)":
            mgmt_passcode = st.text_input("أدخل الكود السري:", type="password")
            if mgmt_passcode == "mgmt999":
                st.success("أهلاً بك في لوحة مؤشرات الإدارة العليا:")
                
                # إضافة الرسم البياني هنا
                chart_data = pd.DataFrame(
                    {"الأعطال المتفاداة": [5, 8, 12, 15, 22, 28]},
                    index=["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"]
                )
                st.markdown("### منحنى انخفاض الأعطال استباقياً")
                st.line_chart(chart_data)
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(label="إجمالي الكفاءة التشغيلية", value="94.8%", delta="+3.2%")
                with col_m2:
                    st.metric(label="الأعطال المتوقعة التي تم تفاديها", value="28 عطل")

    else: # English Section
        st.subheader("Secure Portals for Departments & Management")
        portal_choice = st.radio("Choose Required Portal:", ["IT Sub-divisions", "Upper Management"])
        
        if portal_choice == "Upper Management":
            mgmt_passcode = st.text_input("Enter Upper Management Passcode:", type="password")
            if mgmt_passcode == "mgmt999":
                st.success("Welcome to Upper Management Indicators Dashboard:")
                
                # إضافة الرسم البياني هنا
                chart_data_en = pd.DataFrame(
                    {"Prevented Failures": [5, 8, 12, 15, 22, 28]},
                    index=["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
                )
                st.markdown("### Proactive Failure Reduction Curve")
                st.line_chart(chart_data_en)
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(label="Total Operational Efficiency", value="94.8%", delta="+3.2% proactive")
                with col_m2:
                    st.metric(label="Anticipated Failures Prevented", value="28 Failures")
