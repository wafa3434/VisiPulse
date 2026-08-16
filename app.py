import streamlit as st
import pandas as pd
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# تهيئة بيانات التذاكر
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {"رقم التذكرة": "TICK-101", "معرف الجهاز": "TCH-CH-OPD123", "الأولوية": "قصوى", "الحالة": "قيد المعالجة"}
    ]

# --- الترويسة العليا ---
header_col1, header_col2, header_col3 = st.columns([2, 5, 1])
with header_col3:
    lang = st.selectbox("Language / اللغة", ["العربية (AR)", "English (EN)"])
with header_col1:
    st.markdown("### VisiPulse")
    st.caption("طبقة الذكاء الاستباقي" if lang == "العربية (AR)" else "Proactive Intelligence Layer")
with header_col2:
    st.markdown("<h2 style='text-align: center; color: #1a5276;'>" + 
                ("نظام مراقبة البنية التحتية والإنذار المبكر" if lang == "العربية (AR)" else "Infrastructure Monitoring & Early Warning System") + 
                "</h2>", unsafe_allow_html=True)

st.markdown("---")

# --- التبويبات الرئيسية ---
tab1, tab2, tab3 = st.tabs(["شاشة الموظفين", "بوابة الإدارة العليا", "بوابة تقنية المعلومات (IT)"])

# 1. شاشة الموظفين
with tab1:
    st.subheader("شاشة المستخدم")
    if st.text_input("كود الموظف:", type="password", key="emp_k") == "emp123":
        st.error("تنبيه: عطل استباقي في جهاز TCH-CH-OPD123")
        st.button("تأكيد استلام التنبيه")
    else:
        st.info("يرجى إدخال الكود للوصول للتنبيهات.")

# 2. بوابة الإدارة العليا (كود خاص)
with tab2:
    st.subheader("لوحة مؤشرات الإدارة")
    if st.text_input("كود الإدارة العليا:", type="password", key="mgmt_k") == "mgmt999":
        col_a, col_b = st.columns(2)
        col_a.metric("الأعطال المتفاداة", "28", "+5")
        col_b.metric("نسبة الاستقرار", "94.8%", "+3.2%")
        st.area_chart(pd.DataFrame({"الأداء": [80, 85, 90, 94.8]}))
    else:
        st.warning("وصول مقيد. يتطلب كود الإدارة العليا.")

# 3. بوابة تقنية المعلومات (كود خاص ومختلف)
with tab3:
    st.subheader("لوحة تحكم قسم تقنية المعلومات")
    if st.text_input("كود قسم تقنية المعلومات:", type="password", key="it_k") == "it777":
        # هنا تظهر خيارات الـ IT فقط بعد إدخال كودهم الخاص
        sub_tab = st.selectbox("قسم الـ IT:", ["الجودة", "الأنظمة", "الدعم الفني", "البنية التحتية"])
        
        if sub_tab == "الدعم الفني":
            st.table(pd.DataFrame(st.session_state.tickets))
        elif sub_tab == "البنية التحتية":
            st.write("مراقبة البيئة الفيزيائية (حرارة/طاقة)")
            st.table(pd.DataFrame([{"الجهاز": "Server-01", "الحرارة": "65C"}]))
    else:
        st.warning("وصول مقيد. يتطلب كود قسم تقنية المعلومات.")
