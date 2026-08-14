
import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# --- الترويسة المحسنة مع الشعار ---
header_col1, header_col2, header_col3 = st.columns([2, 5, 1])

with header_col1:
    sub_col_logo, sub_col_text = st.columns([1, 2.5])
    with sub_col_logo:
        try:
            st.image("logo.jpeg", width=70)
        except:
            st.write("VisiPulse")
    with sub_col_text:
        st.markdown("<h3 style='margin-bottom: 0px;'>VisiPulse</h3>", unsafe_allow_html=True)
        st.caption("طبقة الذكاء الاستباقي")

with header_col2:
    st.markdown("<h2 style='text-align: center; color: #1a5276; margin-top: 10px;'>نظام مراقبة البنية التحتية والإنذار المبكر</h2>", unsafe_allow_html=True)

with header_col3:
    lang = st.selectbox("اللغة", ["العربية (AR)", "English (EN)"])

st.markdown("---")

# تبويبات النظام الرئيسية
tab1, tab2 = st.tabs(["شاشة الموظفين والتنبيهات", "بوابة الإدارة والتقنية"])

with tab1:
    st.subheader("شاشة التنبيهات الاستباقية للموظف")
    st.warning("تنبيه استباقي (VisiPulse): تم رصد مؤشرات تراجع في أداء الجهاز المادي (DEV-101). النظام يعالج المشكلة استباقياً.")
    if st.button("ضغط (OK) لتأكيد القراءة"):
        st.success("تم تأكيد الاستلام بنجاح، ومنع تكدس البلاغات العشوائية.")

with tab2:
    portal_choice = st.radio("اختر البوابة المطلوبة:", ["قسم تقنية المعلومات (IT Sub-divisions)", "الإدارة العليا (Upper Management)"])
    
    # بوابة الإدارة العليا
    if portal_choice == "الإدارة العليا (Upper Management)":
        st.markdown("---")
        mgmt_passcode = st.text_input("أدخل الكود السري الخاص بالإدارة العليا:", type="password")
        
        if mgmt_passcode == "mgmt999":
            st.success("أهلاً بك في لوحة مؤشرات الإدارة العليا:")
            st.markdown("### 🎯 لوحة المؤشرات الاستراتيجية")
            
            # 1. رسم بياني لاتجاه الكفاءة العام
            chart_data = pd.DataFrame({"الكفاءة التشغيلية %": [88, 90, 92, 91, 93, 94.8]}, index=["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"])
            st.area_chart(chart_data)
            
            # 2. مؤشرات الأداء (Metrics)
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("إجمالي الأعطال المتفاداة", "28 عطل", "+5")
            col_m2.metric("نسبة الاستقرار العام", "94.8%", "+3.2%")
            col_m3.metric("معدل التوفير المالي", "150 ألف ر.س", "+12%")
            
            st.info("القرار: النظام يحقق مستهدفات الربع الثاني بنجاح، يُوصى بالاستمرار في استراتيجية الصيانة الاستباقية.")

    # بوابة تقنية المعلومات (IT)
    elif portal_choice == "قسم تقنية المعلومات (IT Sub-divisions)":
        st.markdown("---")
        it_passcode = st.text_input("أدخل الكود السري الخاص بقسم الـ IT:", type="password")
        
        if it_passcode == "it123":
            it_sub_tab = st.selectbox("اختر القسم الفرعي المرتبط بالمنظومة:", [
                "مدير الصحة الإلكترونية (e-Health)",
                "قسم الجودة (Quality)",
                "قسم الدعم الفني (IT Support)",
                "قسم الشبكات (Network)"
            ])
            
            # لوحة مدير الصحة الإلكترونية
            if it_sub_tab == "مدير الصحة الإلكترونية (e-Health)":
                st.markdown("### 📊 لوحة مراقبة الصحة الإلكترونية (e-Health)")
                data = pd.DataFrame({'الجاهزية %': [99.2, 98.5, 99.8, 99.5]}, index=["سيرفر 1", "سيرفر 2", "سيرفر 3", "سيرفر 4"])
                st.bar_chart(data)
                st.success("القرار: الأنظمة تعمل بكفاءة عالية، لا حاجة لإيقاف أي خدمات.")

            # لوحة مدير الجودة
            elif it_sub_tab == "قسم الجودة (Quality)":
                st.markdown("### 📈 لوحة جودة البيانات وحوكمتها (Quality)")
                chart_data = pd.DataFrame(
                    {"زمن الاستجابة الفعلي": [2.1, 1.8, 3.2, 2.5], "المستهدف (Target)": [2.0, 2.0, 2.0, 2.0]},
                    index=["وحدة 1", "وحدة 2", "وحدة 3", "وحدة 4"]
                )
                st.line_chart(chart_data)
                st.error("تنبيه: الوحدة 3 و 4 تجاوزت المستهدف. القرار: مطلوب تدخل تصحيحي.")
            
            # باقي الأقسام تشغيلية
            else:
                st.info(f"أنت الآن في: {it_sub_tab}. اللوحة التشغيلية قيد التحديث.")
        
        elif it_passcode:
            st.error("الكود السري غير صحيح.")
