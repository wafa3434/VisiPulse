import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="VisiPulse - Advanced IT System", layout="wide")

def generate_stats_excel():
    data = {
        "اسم الجهاز": ["DEV-101", "SRV-02", "DEV-305"],
        "نوع العطل": ["هارد ديسك", "حرارة", "برمجيات"],
        "عدد مرات التعطل": [3, 5, 2],
        "الشركة المسؤولة": ["سيسكو", "إنتل", "داخلية"]
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Statistics")
    return output.getvalue()

def it_portal():
    st.subheader("لوحة تحكم تقنية المعلومات المتقدمة")
    section = st.selectbox("اختر القسم:", ["الدعم الفني", "إدارة الجودة", "الأنظمة والتطبيقات"])
    
    if section == "الدعم الفني":
        st.write("---")
        contractor = st.text_input("اسم الشركة المقاوله (اضغط Enter للتأكيد):")
        
        maintenance_type = st.radio("هل يحتاج الجهاز صيانة خارجية؟", ["لا (داخلي)", "نعم (تحويل للشركة)"])
        
        if maintenance_type == "نعم (تحويل للشركة)":
            st.error(f"تنبيه: تم تفعيل بروتوكول التحويل الخارجي لـ {contractor if contractor else 'الشركة المحددة'}")
            
        if st.button("استخراج تقرير الأعطال الدوري (Excel)"):
            excel_data = generate_stats_excel()
            st.download_button("تحميل التقرير", data=excel_data, file_name="Maintenance_Stats.xlsx")

    elif section == "إدارة الجودة":
        st.subheader("رسم بياني: كفاءة الأجهزة")
        chart_data = pd.DataFrame(np.random.randn(10, 2), columns=['أداء المعالج', 'استقرار النظام'])
        st.area_chart(chart_data)

    elif section == "الأنظمة والتطبيقات":
        st.subheader("حالة الأنظمة الحالية")
        st.bar_chart({"زمن الاستجابة (ms)": [50, 120, 80, 210]})
        st.success("الأنظمة تعمل بكفاءة 98%.")

tab1, tab2, tab3 = st.tabs(["شاشة الموظفين", "بوابة الإدارة", "بوابة الـ IT"])

with tab3:
    if st.text_input("كود الدخول للـ IT:", type="password") == "it123":
        it_portal()
    else:
        st.warning("يرجى إدخال كود الدخول الصحيح.")
