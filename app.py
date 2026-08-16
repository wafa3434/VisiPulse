import streamlit as st
import pandas as pd
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse", layout="wide")

# 1. إظهار الشعار (تأكدي أن الملف باسم logo.jpeg في نفس المجلد)
def show_header():
    col_l, col_m, col_r = st.columns([1, 4, 1])
    with col_l:
        try:
            st.image("logo.jpeg", width=80)
        except:
            st.write("LOGO")
    with col_m:
        st.title("VisiPulse")
        st.caption("طبقة الذكاء الاستباقي - Infrastructure Monitoring")

show_header()
st.markdown("---")

# 2. تبويبات النظام
tab1, tab2, tab3 = st.tabs(["شاشة الموظفين", "بوابة الإدارة العليا", "بوابة تقنية المعلومات"])

# شاشة الموظف مع Pop-up
with tab1:
    st.subheader("شاشة الموظف")
    if st.text_input("كود الموظف:", type="password") == "emp123":
        # هذا هو الـ Pop-up (Toast)
        st.toast("تنبيه استباقي: تم رصد خلل في الهارد ديسك لجهازك (TCH-CH-OPD123). تم إبلاغ قسم الدعم الفني.", icon="⚠️")
        st.warning("جاري التنسيق مع الدعم الفني لإصلاح الخلل.")
    else:
        st.info("يرجى إدخال كود الموظف.")

# بوابة الإدارة العليا
with tab2:
    if st.text_input("كود الإدارة:", type="password") == "mgmt999":
        st.subheader("لوحة المؤشرات الاستراتيجية")
        st.metric("نسبة الأعطال التي تم تلافيها", "98%")
    else:
        st.warning("دخول مقيد")

# بوابة الـ IT (هنا تُعرض تفاصيل الأعطال)
with tab3:
    if st.text_input("كود الـ IT:", type="password") == "it777":
        st.subheader("لوحة تحكم الدعم الفني (سجل الأعطال)")
        
        # تصنيف الأعطال هنا
        faults_df = pd.DataFrame({
            "الجهاز": ["TCH-CH-OPD123", "TCH-CH-ER005"],
            "نوع العطل": ["هارد ديسك (مادي)", "فيروس (تقني)"],
            "الإجراء": ["استبدال قطعة", "تنظيف برمجي"]
        })
        st.table(faults_df)
    else:
        st.warning("دخول مقيد")
