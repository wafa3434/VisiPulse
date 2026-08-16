import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# وظيفة تصدير الإحصائيات والأعطال إلى إكسل
def generate_stats_excel():
    data = {
        "اسم الجهاز": ["DEV-101", "SRV-02", "DEV-305"],
        "نوع العطل": ["هارد ديسك", "حرارة المعالج", "برمجيات"],
        "عدد مرات التعطل": [3, 5, 2],
        "الشركة المسؤولة": ["سيسكو", "إنتل", "داخلية"]
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Maintenance_Statistics")
    return output.getvalue()

# --- الترويسة العليا (شعار + ترجمة) ---
header_col1, header_col2, header_col3 = st.columns([2, 5, 1])

with header_col3:
    lang = st.selectbox("Language / اللغة", ["العربية (AR)", "English (EN)"])

with header_col1:
    sub_col_logo, sub_col_text = st.columns([1, 2.5])
    with sub_col_logo:
        try:
            st.image("logo.jpeg", width=70)
        except:
            st.write("VisiPulse")
    with sub_col_text:
        st.markdown("<h3 style='margin-bottom: 0px;'>VisiPulse</h3>", unsafe_allow_html=True)
        st.caption("طبقة الذكاء الاستباقي" if lang == "العربية (AR)" else "Proactive Intelligence Layer")

with header_col2:
    st.markdown("<h2 style='text-align: center; color: #1a5276; margin-top: 10px;'>" + 
                ("نظام مراقبة البنية التحتية والإنذار المبكر" if lang == "العربية (AR)" else "Infrastructure Monitoring & Early Warning System") + 
                "</h2>", unsafe_allow_html=True)

st.markdown("---")

# --- التبويبات الرئيسية ---
tab1, tab2, tab3 = st.tabs(["شاشة الموظفين", "بوابة الإدارة العليا", "بوابة تقنية المعلومات (IT)"])

# 1. شاشة الموظفين
with tab1:
    st.subheader("شاشة التنبيهات الاستباقية للموظف")
    st.error("تنبيه: تم رصد خلل في الهارد ديسك أو المعالج للجهاز (DEV-305).")
    if st.button("إرسال التذكرة تلقائياً إلى الـ IT"):
        st.success("تم إرسال التذكرة بنجاح!")
    st.info("نصيحة: يرجى عمل نسخة احتياطية لملفاتك الحساسة.")

# 2. بوابة الإدارة العليا
with tab2:
    mgmt_pass = st.text_input("أدخل كود الإدارة:", type="password", key="mgmt_key")
    if mgmt_pass == "mgmt999":
        st.subheader("لوحة المؤشرات الاستراتيجية وأداء المستشفى")
        c1, c2, c3 = st.columns(3)
        c1.metric("الأعطال التي تم تلافيها", "28 عطل", "+5")
        c2.metric("نسبة الاستقرار العام", "94.8%", "+3.2%")
        c3.metric("التوفير المالي", "150 ألف ر.س", "+12%")
        st.area_chart(pd.DataFrame({"الأداء التشغيلي": [88, 90, 92, 91, 93, 94.8]}))
    elif mgmt_pass:
        st.warning("كود الإدارة غير صحيح.")

# 3. بوابة تقنية المعلومات (IT)
with tab3:
    it_pass = st.text_input("أدخل كود الـ IT:", type="password", key="it_key")
    if it_pass == "it123":
        sub_tab = st.selectbox("اختر القسم:", [
            "الدعم الفني", 
            "البنية التحتية (حرارة وطاقة)", 
            "إدارة الصحة الإلكترونية", 
            "الأنظمة والتطبيقات"
        ])
        
        # أ. الدعم الفني
        if "الدعم الفني" in sub_tab:
            st.subheader("إدارة البلاغات والصيانة الخارجية")
            contractor = st.text_input("اسم الشركة المقاوله (اضغط Enter للتأكيد):")
            if contractor:
                st.success(f"تم ربط التذاكر بالشركة المقاولة: {contractor}")
            
            maintenance_type = st.radio("هل يحتاج الجهاز صيانة خارجية؟", ["لا (داخلي)", "نعم (تحويل للشركة)"])
            if maintenance_type == "نعم (تحويل للشركة)":
                st.error(f"تنبيه: تم توجيه الجهاز فوراً للشركة المقاولة ({contractor if contractor else 'الخارجية'}) بناءً على نوع العطل.")
            
            st.write("---")
            if st.button("استخراج تقرير الأعطال الدوري (Excel)"):
                excel_data = generate_stats_excel()
                st.download_button("تحميل التقرير الدوري", data=excel_data, file_name="Maintenance_Stats.xlsx")
        
        # ب. البنية التحتية (حرارة المعالجات والكهرباء)
        elif "البنية التحتية" in sub_tab:
            st.subheader("المراقبة الاستباقية للحرارة والطاقة في الداتا سنتر")
            
            cpu_data = pd.DataFrame({
                "السيرفر": ["SRV-01", "SRV-02", "SRV-03"],
                "حرارة المعالج (C)": [65, 88, 72],
                "حالة المعالج": ["آمن", "تجاوز الحد المسموح (خطر)", "آمن"]
            })
            st.table(cpu_data)
            
            if cpu_data["حرارة المعالج (C)"].max() > 80:
                st.error("تنبيه استباقي: تم رصد ارتفاع في حرارة المعالج للسيرفر SRV-02 وتم تشغيل نظام التبريد الطارئ تلقائياً.")
            
            st.write("---")
            st.markdown("#### تأثير الكهرباء وشبكة الطاقة (UPS)")
            power_data = pd.DataFrame({
                "وحدة الطاقة": ["UPS-A (غرفة الخوادم)", "UPS-B (الأقسام الطبية)"],
                "استقرار الجهد (V)": [220, 218],
                "استقرار الحمل %": [98, 95]
            })
            st.table(power_data)
            st.metric("مؤشر استقرار شبكة الكهرباء العام", "96.5%", "+0.5%")
            
        # ج. إدارة الصحة الإلكترونية (ويتبع لها قسم الجودة كخيار فرعي)
        elif "إدارة الصحة الإلكترونية" in sub_tab:
            st.subheader("إدارة الصحة الإلكترونية والتحول الرقمي")
            
            # الخيار الفرعي لإدارة الجودة تحت الصحة الإلكترونية
            health_sub_section = st.radio("اختر الوحدة:", ["مؤشرات الصحة الإلكترونية العامة", "وحدة الجودة (Quality Management Unit)"])
            
            if "وحدة الجودة" in health_sub_section:
                st.markdown("#### لوحة القرار الاستباقي لوحدة الجودة")
                st.info("الاستباقية: يحلل النظام سجلات الأخطاء الطبية الرقمية لتجنب تكرارها وتحسين الـ SLA تلقائياً.")
                
                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    st.markdown("##### نسبة الالتزام بأوقات معالجة البلاغات (SLA %)")
                    st.bar_chart(pd.DataFrame({"الالتزام %": [92, 88, 95, 91]}, index=["الربع الأول", "الربع الثاني", "الربع الثالث", "الربع الرابع"]))
                with col_q2:
                    st.markdown("##### مؤشر رضا المستفيدين")
                    st.line_chart(pd.DataFrame({"الرضا": [85, 89, 93, 96]}, index=["يناير", "فبراير", "مارس", "أبريل"]))
                
                decision_input = st.text_input("اكتب قرار الجودة المعتمد ثم اضغط Enter:")
                if decision_input:
                    st.success(f"تم توثيق واختبار قرار الجودة آلياً: {decision_input}")
            else:
                st.bar_chart(pd.DataFrame({'معدل التكامل الرقمي %': [99.2, 98.5, 99.8, 99.5]}, index=["الربط المركزي", "السجلات الصحية", "الخدمات الإكلينيكية", "التكامل الإحصائي"]))
                st.success("الاستباقية: مراقبة مستمرة لتكامل الأنظمة الطبية لمنع أي انقطاع في مزامنة بيانات المرضى.")
            
        # د. الأنظمة والتطبيقات
        elif "الأنظمة والتطبيقات" in sub_tab:
            st.subheader("مراقبة أداء الأنظمة والتطبيقات الطبية (APIs & Systems)")
            st.info("الاستباقية: التنبؤ بتكدس البيانات وضغط الطلبات على السيرفرات قبل حدوث بطء في النظام الطبي (+Oasis).")
            
            app_status_df = pd.DataFrame({
                "النظام / التطبيق": ["النظام الطبي (+Oasis)", "نظام إدارة المواعيد", "نظام المختبر والاشعة LIS/PACS"],
                "حالة استقرار الأداء": ["مستقر (تحت المراقبة)", "مستقر", "تحذير: ضغط عالي متوقع"],
                "التوصية الاستباقية": ["توسعة الذاكرة مؤقتاً", "جدولة التحديثات ليلاً", "إعادة توجيه الأحمال"]
            })
            st.table(app_status_df)
            
            st.bar_chart(pd.DataFrame({"زمن الاستجابة المتوقع (ms)": [50, 120, 80, 210]}, index=["النظام الطبي", "المواعيد", "المختبر", "الأشعة"]))
            st.warning("تنبيه استباقي للأنظمة: تم تفعيل موازنة الأحمال الآلية (Load Balancing) على نظام المختبرات لتجنب توقف الخدمة.")
            
    elif it_pass:
        st.warning("كود الـ IT غير صحيح. استخدم it123")
