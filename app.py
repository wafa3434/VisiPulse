import streamlit as st
import pandas as pd
import numpy as np

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# --- الترويسة ---
header_col1, header_col2, header_col3 = st.columns([1.5, 3.5, 1])
with header_col1:
    st.markdown("### **VisiPulse**")
with header_col3:
    lang = st.selectbox("Language / اللغة", ["العربية (AR)", "English (EN)"])

st.markdown("---")

tab1, tab2 = st.tabs(["شاشة الموظفين", "بوابة الإدارة والتقنية"])

with tab1:
    st.warning("تنبيه استباقي (VisiPulse): تم رصد مؤشرات تراجع في أداء الجهاز (DEV-101).")

with tab2:
    portal_choice = st.radio("اختر البوابة:", ["قسم تقنية المعلومات (IT)", "الإدارة العليا (Upper Management)"])
    
    if portal_choice == "قسم تقنية المعلومات (IT)":
        it_passcode = st.text_input("أدخل كود الـ IT:", type="password")
        if it_passcode == "it123":
            sub_tab = st.selectbox("اختر القسم:", ["مدير الصحة الإلكترونية (e-Health)", "قسم الجودة (Quality)", "قسم الشبكات (Network)", "الدعم الفني (IT Support)"])
            
            # --- تعديل: إضافة رسوم بيانية لمدير الصحة والجودة ---
            if sub_tab == "مدير الصحة الإلكترونية (e-Health)":
                st.markdown("### لوحة مراقبة الصحة الإلكترونية (Strategic View)")
                # رسم بياني لمؤشر الجاهزية
                data = pd.DataFrame({'الجاهزية %': [99.2, 98.5, 99.8, 99.5]}, index=["سيرفر 1", "سيرفر 2", "سيرفر 3", "سيرفر 4"])
                st.bar_chart(data)
                st.success("القرار: الأنظمة تعمل بكفاءة عالية، لا حاجة لإيقاف أي خدمات.")

            elif sub_tab == "قسم الجودة (Quality)":
                st.markdown("### لوحة جودة البيانات (Performance vs Target)")
                # رسم بياني مقارنة زمن الاستجابة بالمستهدف
                chart_data = pd.DataFrame(
                    {"زمن الاستجابة الفعلي": [2.1, 1.8, 3.2, 2.5], "المستهدف (Target)": [2.0, 2.0, 2.0, 2.0]},
                    index=["وحدة 1", "وحدة 2", "وحدة 3", "وحدة 4"]
                )
                st.line_chart(chart_data)
                st.error("تنبيه: الوحدة 3 و 4 تجاوزت المستهدف. القرار: مطلوب تدخل تصحيحي.")
            
            else:
                st.info("لوحة تشغيلية: بانتظار تحديثات النظام.")

    elif portal_choice == "الإدارة العليا (Upper Management)":
        mgmt_passcode = st.text_input("أدخل كود الإدارة العليا:", type="password")
        if mgmt_passcode == "mgmt999":
            st.markdown("### لوحة مؤشرات الإدارة العليا")
            chart_data = pd.DataFrame({"الأعطال المتفاداة": [5, 8, 12, 15, 22, 28]}, index=["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"])
            st.line_chart(chart_data)
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("الكفاءة التشغيلية", "94.8%", "+3.2%")
            col_m2.metric("الأعطال المتفاداة", "28 عطل")
