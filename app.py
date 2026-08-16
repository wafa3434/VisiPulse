import streamlit as st
import pandas as pd
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# تهيئة بيانات التذاكر في الذاكرة
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {"التذكرة": "TICK-101", "الجهاز": "DEV-101", "الوصف": "تراجع أداء الهارد ديسك", "الحالة": "قيد المعالجة"}
    ]

# وظيفة تصدير التقارير (Excel)
def export_to_excel(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in data_dict.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# --- الترويسة العليا ---
def show_header():
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            st.image("logo.jpeg", width=100)
        except:
            st.write("VisiPulse")
    with col2:
        st.title("VisiPulse")
        st.caption("طبقة الذكاء الاستباقي | Infrastructure Monitoring & Early Warning System")

show_header()
st.markdown("---")

# --- التبويبات ---
tab1, tab2, tab3 = st.tabs(["شاشة الموظفين", "بوابة الإدارة العليا", "بوابة تقنية المعلومات (IT)"])

# 1. شاشة الموظفين (مفتوحة - تنبيه مباشر)
with tab1:
    st.subheader("لوحة التنبيهات الاستباقية للموظف")
    st.error("⚠️ تنبيه استباقي: رصد خلل في الهارد ديسك لجهازك (DEV-305).")
    if st.button("إرسال تذكرة صيانة (Ticket)"):
        st.success("تم إرسال التذكرة تلقائياً إلى قسم الدعم الفني!")
    st.info("💡 نصيحة: يرجى عمل نسخة احتياطية لبياناتك فوراً.")

# 2. بوابة الإدارة العليا (مقيدة بكود)
with tab2:
    if st.text_input("كود الدخول للإدارة:", type="password", key="mgmt_login") == "mgmt999":
        st.subheader("مؤشرات الأداء الاستراتيجية")
        col_a, col_b = st.columns(2)
        col_a.metric("الأعطال التي تم تلافيها", "42", "+12%")
        col_b.metric("الوفر المالي (الصيانة الوقائية)", "150k SAR", "+5%")
        st.area_chart(pd.DataFrame({"الأداء": [80, 85, 90, 94.8]}))
    else:
        st.warning("يرجى إدخال كود الإدارة للوصول.")

# 3. بوابة تقنية المعلومات (IT - مقيدة بكود)
with tab3:
    if st.text_input("كود الدخول للـ IT:", type="password", key="it_login") == "it777":
        sub = st.selectbox("اختر القسم:", ["إدارة الصحة الإلكترونية", "الدعم الفني", "البنية التحتية"])
        
        if sub == "الدعم الفني":
            st.table(pd.DataFrame(st.session_state.tickets))
            
        elif sub == "البنية التحتية":
            st.subheader("مراقبة الحرارة والطاقة (استباقي)")
            cpu_df = pd.DataFrame({"السيرفر": ["SRV-01", "SRV-02"], "الحرارة (C)": [65, 88], "الحالة": ["آمن", "خطر"]})
            st.table(cpu_df)
            
            # منطق الاستباقية للحرارة
            if cpu_df["الحرارة (C)"].max() > 80:
                st.error("⚠️ تحذير: السيرفر SRV-02 يتجاوز الحرارة المسموحة!")
            
            st.write("---")
            st.metric("استقرار شبكة الكهرباء (UPS)", "96%", "-2%")
            
            # التصدير للإكسل
            excel_data = export_to_excel({" الحرارة": cpu_df, "الطاقة": pd.DataFrame({"UPS": ["UPS-A"], "Load %": [96]})})
            st.download_button("📥 تحميل التقرير الدوري (Excel)", data=excel_data, file_name="IT_Infrastructure_Report.xlsx")
    else:
        st.warning("يرجى إدخال كود الـ IT للوصول.")
