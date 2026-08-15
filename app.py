import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# تهيئة الذاكرة المؤقتة (Session State) لحفظ البلاغات التلقائية الواردة لقسم الـ IT
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {"رقم التذكرة": "TICK-101", "الجهاز": "DEV-101", "نوع العطل": "مادي (Hardware)", "الوصف": "تراجع أداء المكونات المادية والهارد ديسك", "الحالة": "قيد المعالجة"},
        {"رقم التذكرة": "TICK-102", "الجهاز": "DEV-204", "نوع العطل": "أمني / تقني", "الوصف": "تم رصد فيروس أو تهديد محتمل في الجهاز", "الحالة": "جديد"}
    ]

# حالة للتحقق مما إذا تم الضغط على زر الإنذار أم لا
if "alert_acknowledged" not in st.session_state:
    st.session_state.alert_acknowledged = False

# --- الترويسة العليا (شعار + ترجمة) ---
header_col1, header_col2, header_col3 = st.columns([2, 5, 1])

with header_col3:
    lang = st.selectbox("Language / اللغة", ["العربية (AR)", "English (EN)"])

with header_col1:
    sub_col_logo, sub_col_text = st.columns([1, 2.5])
    with sub_col_logo:
        try: st.image("logo.jpeg", width=70)
        except: st.write("VisiPulse")
    with sub_col_text:
        st.markdown("<h3 style='margin-bottom: 0px;'>VisiPulse</h3>", unsafe_allow_html=True)
        st.caption("طبقة الذكاء الاستباقي" if lang == "العربية (AR)" else "Proactive Intelligence Layer")

with header_col2:
    st.markdown("<h2 style='text-align: center; color: #1a5276; margin-top: 10px;'>" + 
                ("نظام مراقبة البنية التحتية والإنذار المبكر" if lang == "العربية (AR)" else "Infrastructure Monitoring & Early Warning System") + 
                "</h2>", unsafe_allow_html=True)

st.markdown("---")

# --- تبويبات النظام ---
tab_titles = ["شاشة الموظفين والتنبيهات", "بوابة الإدارة والتقنية"] if lang == "العربية (AR)" else ["Employee Alerts", "Management & IT Portal"]
tab1, tab2 = st.tabs(tab_titles)

with tab1:
    st.subheader("شاشة التنبيهات الاستباقية للموظف" if lang == "العربية (AR)" else "Employee Proactive Alert Screen")
    
    # محاكاة الإنذار الاستباقي الفوري على الواجهة دون الحاجة لإدخال يدوي
    if not st.session_state.alert_acknowledged:
        st.error("⚠️ انتبه: يتواجد فيروس في الجهاز أو الهارد ديسك لا يعمل بشكل سليم (DEV-305). يرجى تأكيد الإرسال لقسم الـ IT.")
        
        if st.button("OK - إرسال التذكرة تلقائياً إلى الـ IT" if lang == "العربية (AR)" else "OK - Send Ticket Automatically to IT"):
            # إضافة التذكرة تلقائياً للنظام
            auto_ticket = {
                "رقم التذكرة": f"TICK-{len(st.session_state.tickets) + 101}",
                "الجهاز": "DEV-305",
                "نوع العطل": "أمني / تقني (Security/Hardware)",
                "الوصف": "إنذار استباقي: فيروس بالهارد ديسك / عطل معالجة",
                "الحالة": "جديد (New)"
            }
            st.session_state.tickets.append(auto_ticket)
            st.session_state.alert_acknowledged = True
            st.rerun()
    else:
        st.success("✅ تم تأكيد الإنذار وإرسال التذكرة بنجاح إلى قسم تقنية المعلومات (IT). شكراً لتعاونك." if lang == "العربية (AR)" else "✅ Alert acknowledged and ticket sent to IT successfully.")
        
        if st.button("إعادة عرض الإنذار للاختبار" if lang == "العربية (AR)" else "Reset Alert for Testing"):
            st.session_state.alert_acknowledged = False
            st.rerun()

with tab2:
    portal_label = "اختر البوابة:" if lang == "العربية (AR)" else "Choose Portal:"
    portals = ["قسم تقنية المعلومات (IT)", "الإدارة العليا (Upper Management)"] if lang == "العربية (AR)" else ["IT Department", "Upper Management"]
    portal_choice = st.radio(portal_label, portals)
    
    # بوابة الإدارة العليا
    if "الإدارة العليا" in portal_choice or "Upper Management" in portal_choice:
        mgmt_passcode = st.text_input("أدخل كود الإدارة:" if lang == "العربية (AR)" else "Enter Password:", type="password", key="mgmt_pass")
        if mgmt_passcode == "mgmt999":
            st.markdown("### " + ("لوحة المؤشرات الاستراتيجية وأداء المستشفى" if lang == "العربية (AR)" else "Strategic Indicators Dashboard"))
            chart_data = pd.DataFrame({"الكفاءة التشغيلية %": [88, 90, 92, 91, 93, 94.8]}, index=["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"] if lang == "العربية (AR)" else ["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
            st.area_chart(chart_data)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الأعطال المتفاداة" if lang == "العربية (AR)" else "Failures Prevented", "28 عطل", "+5")
            c2.metric("نسبة الاستقرار العام" if lang == "العربية (AR)" else "Stability Rate", "94.8%", "+3.2%")
            c3.metric("التوفير المالي" if lang == "العربية (AR)" else "Financial Savings", "150 ألف ر.س", "+12%")

    # بوابة تقنية المعلومات (IT)
    elif "قسم تقنية المعلومات" in portal_choice or "IT Department" in portal_choice:
        it_passcode = st.text_input("أدخل كود الـ IT:" if lang == "العربية (AR)" else "Enter IT Password:", type="password", key="it_pass")
        if it_passcode == "it123":
            
            if lang == "العربية (AR)":
                sub_tabs = [
                    "مدير الصحة الإلكترونية (e-Health)",
                    "قسم الأنظمة الطبية (Medical System)",
                    "قسم الدعم الفني (IT Support)",
                    "قسم الشبكات (Network)",
                    "قسم الجودة (Quality)"
                ]
            else:
                sub_tabs = [
                    "e-Health Manager",
                    "Medical System",
                    "IT Support",
                    "Network",
                    "Quality Department"
                ]
                
            sub_tab = st.selectbox("اختر القسم الفرعي:" if lang == "العربية (AR)" else "Select Sub-division:", sub_tabs)
            
            # 1. الصحة الإلكترونية
            if "e-Health" in sub_tab or "الصحة الإلكترونية" in sub_tab:
                st.markdown("### لوحة مراقبة الصحة الإلكترونية (e-Health)")
                st.bar_chart(pd.DataFrame({'الجاهزية %': [99.2, 98.5, 99.8, 99.5]}, index=["سيرفر 1", "سيرفر 2", "سيرفر 3", "سيرفر 4"]))
                st.success("آلية الاستفادة: مراقبة التوافق الرقمي وتكامل الأنظمة المساندة وضمان استمرارية الخدمات.")

            # 2. الأنظمة الطبية
            elif "Medical" in sub_tab or "الأنظمة الطبية" in sub_tab:
                st.markdown("### لوحة الأنظمة الطبية (Medical System)")
                st.info("الفكرة الاستباقية: مراقبة مساحات تخزين السيرفرات وسرعة استجابة النظام الطبي دون إبطائه.")
                st.success("القيمة المضافة: ضمان استقرار بيئة العمل الطبية وتدفق العمليات الإكلينيكية بسلاسة تامة.")
                
                med_data = pd.DataFrame({"سرعة الاستجابة (ms)": [120, 115, 130, 110, 105]}, index=["وحدة العناية", "الطوارئ", "العيادات", "الأشعة", "المختبر"])
                st.line_chart(med_data)

            # 3. الدعم الفني (استقبال التذاكر التلقائية وتوجيهها لشركة الصيانة)
            elif "IT Support" in sub_tab or "الدعم الفني" in sub_tab:
                st.markdown("### لوحة تحكم قسم الدعم الفني والتنبؤ بالأعطال")
                st.info("الفكرة الاستباقية: استقبال التذاكر المرصودة استباقياً وتتبعها لخفض تكاليف وصيانة الأجهزة.")
                
                contractor = st.text_input("أدخل اسم الشركة المقاولة للصيانة (ثم اضغط Enter):" if lang == "العربية (AR)" else "Enter Maintenance Contractor Name (Press Enter):")
                
                if contractor:
                    st.success(f"تم ربط التذاكر الواردة وإرسالها تلقائياً إلى شركة الصيانة: {contractor}")
                
                st.markdown("#### سجل البلاغات الواردة تلقائياً من الأجهزة (الإنذار الاستباقي):")
                tickets_df = pd.DataFrame(st.session_state.tickets)
                if contractor:
                    tickets_df["الشركة المقاولة"] = contractor
                st.table(tickets_df)

            # 4. الشبكات
            elif "Network" in sub_tab or "الشبكات" in sub_tab:
                st.markdown("### لوحة مراقبة الشبكات (Network)")
                st.info("الفكرة الاستباقية: تحليل أوقات الذروة واستهلاك النطاق الترددي لتوزيع الأحمال استباقياً وتقليل الاختناقات الرقمية.")
                
                net_data = pd.DataFrame({"استهلاك النطاق (Mbps)": [45, 70, 95, 60, 40]}, index=["الصباح", "الظهر", "أوقات الذروة", "المساء", "الليل"])
                st.area_chart(net_data)
                st.success("القرار الاستباقي: تم إعادة توجيه الأحمال آلياً لتجنب أي هبوط في سرعة الشبكة.")

            # 5. الجودة
            elif "Quality" in sub_tab or "الجودة" in sub_tab:
                st.markdown("### لوحة جودة البيانات وحوكمتها (Quality)")
                st.line_chart(pd.DataFrame({"زمن الاستجابة الفعلي": [2.1, 1.8, 3.2, 2.5], "المستهدف": [2.0, 2.0, 2.0, 2.0]}, index=["وحدة 1", "وحدة 2", "وحدة 3", "وحدة 4"]))
                st.error("تنبيه: مراقبة أزمنة الاستجابة لحظياً وإطلاق علامات حمراء عند تجاوز المستهدفات لضمان الامتثال للمعايير.")
