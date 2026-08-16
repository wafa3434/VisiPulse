السبب أن التذكرة لا تظهر بشكل صحيح يرجع لأن كود زر الإرسال كان يعيد تحميل الشاشة (Rerun) بدون حفظ التذكرة بشكل دائم في الذاكرة المشتركة (st.session_state) بالطريقة الصحيحة للزر، أو أن المفاتيح تتداخل.
تفضلي الكود المعدل بالكامل (نسخ ولصق)، حيث قمت بربط زر إرسال التذكرة من شاشة الموظفين بشكل مباشر مع جدول التذاكر في قسم الدعم الفني باستخدام دالة st.form أو تحديث دقيق للـ session_state لتظهر التذكرة فوراً وبدون أي مشاكل:
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# تهيئة تخزين التذاكر في الـ Session State لضمان مزامنتها بين الشاشات
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {"الجهاز": "DEV-305", "نوع العطل": "صيانة خارجية (هارد ديسك تالف)", "الحالة": "مفتوحة وعاجلة"},
        {"الجهاز": "SRV-01", "نوع العطل": "صيانة داخلية (تحديث برمجيات)", "الحالة": "مكتملة"}
    ]

# وظيفة تصدير الأعطال كملف CSV
def generate_stats_csv():
    data = {
        "اسم الجهاز": ["DEV-101", "SRV-02", "DEV-305"],
        "نوع العطل": ["هارد ديسك", "حرارة المعالج", "صيانة خارجية (هارد ديسك تالف)"],
        "عدد مرات التعطل": [3, 5, 2],
        "الشركة المسؤولة": ["سيسكو", "إنتل", "شركة الصيانة الخارجية"]
    }
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8-sig')

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
    
    # استخدام نموذج (Form) لضمان حفظ وإرسال التذكرة للـ IT بدون فقدان البيانات عند التحديث
    with st.form("employee_ticket_form"):
        emp_maintenance_choice = st.radio(
            "حدد نوع الإصلاح المطلوب:", 
            ["صيانة داخلية", "صيانة خارجية (تحويل للشركة المقاولة)"]
        )
        submitted = st.form_submit_button("إرسال التذكرة تلقائياً إلى الـ IT")
        
        if submitted:
            fault_type_str = "صيانة خارجية (هارد ديسك تالف)" if "صيانة خارجية" in emp_maintenance_choice else "صيانة داخلية (عطل بسيط)"
            new_ticket = {"الجهاز": "DEV-305", "نوع العطل": fault_type_str, "الحالة": "مفتوحة وعاجلة"}
            
            # إضافة التذكرة مباشرة للقائمة المعروضة في قسم الـ IT
            st.session_state.tickets.append(new_ticket)
            st.success("تم إرسال التذكرة بنجاح إلى قسم الدعم الفني!")
        
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
        ], key="it_sub_tabs_key")
        
        # أ. الدعم الفني
        if "الدعم الفني" in sub_tab:
            st.subheader("إدارة البلاغات وتوجيه أعطال الصيانة الخارجية للشركات")
            
            st.info("الاستباقية: يحلل النظام سجل الأعطال لتوقع قطع الغيار التي ستنفد قريباً بناءً على معدل الاستهلاك.")
            prediction_df = pd.DataFrame({
                "قطعة الغيار / المكون": ["هارد ديسك SSD 512GB", "وذاكرة عشوائية RAM 16GB", "مزود طاقة PSU"],
                "المخزون الحالي": ["2 قطع", "1 قطع (منخفض جداً)", "5 قطع"],
                "التوصية الاستباقية الفورية": ["طلب شراء عاجل", "تنبيه: طلب توريد فوري لتجنب توقف الصيانة", "المخزون آمن"]
            })
            st.table(prediction_df)
            st.warning("تنبيه استباقي للدعم الفني: تم رصد نقص وشيك في وحدات الذاكرة العشوائية (RAM)، وتم إنشاء مسودة طلب شراء آليا.")
            
            st.write("---")
            st.markdown("#### كافة التذاكر الواردة من الموظفين (تحدث لحظياً):")
            
            # عرض التذاكر المحدثة مباشرة من الذاكرة المشتركة
            tickets_df = pd.DataFrame(st.session_state.tickets)
            st.table(tickets_df)
            
            st.write("---")
            contractor = st.text_input("اسم الشركة المقاوله (اضغط Enter للتأكيد):", key="contractor_input_key")
            
            # فلترة التذاكر الخاصة بالصيانة الخارجية فقط لتوجيهها للشركة
            external_tickets = [t for t in st.session_state.tickets if "صيانة خارجية" in t["نوع العطل"]]
            
            if external_tickets:
                st.warning(f"يوجد {len(external_tickets)} تذكرة مصنفة كـ 'صيانة خارجية' وتتطلب التحويل للشركة المقاولة.")
                if contractor:
                    st.success(f"تم إرسال أعطال الصيانة الخارجية رسمياً إلى الشركة المقاولة: {contractor}")
            else:
                st.info("لا توجد أعطال صيانة خارجية تتطلب التحويل للشركة حالياً.")
            
            st.write("---")
            if st.button("استخراج تقرير الأعطال الدوري (CSV)", key="csv_export_btn"):
                csv_data = generate_stats_csv()
                st.download_button("تحميل التقرير الدوري", data=csv_data, file_name="Maintenance_Stats.csv", mime="text/csv")
        
        # ب. البنية التحتية
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
            
        # ج. إدارة الصحة الإلكترونية والجودة
        elif "إدارة الصحة الإلكترونية" in sub_tab:
            st.subheader("إدارة الصحة الإلكترونية والتحول الرقمي")
            health_sub_section = st.radio("اختر الوحدة:", ["مؤشرات الصحة الإلكترونية العامة", "وحدة الجودة (Quality Management Unit)"], key="health_sub_radio")
            
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
                
                decision_input = st.text_input("اكتب قرار الجودة المعتمد ثم اضغط Enter:", key="quality_decision_key")
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
