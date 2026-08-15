import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# تهيئة الذاكرة المؤقتة (Session State) للبلاغات الواردة
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {"رقم التذكرة": "TICK-101", "الجهاز": "DEV-101", "القسم المستهدف": "قسم الدعم الفني", "الوصف": "تراجع أداء الهارد ديسك", "الحالة": "قيد المعالجة"},
        {"رقم التذكرة": "TICK-102", "الجهاز": "DEV-204", "القسم المستهدف": "قسم الدعم الفني", "الوصف": "إنذار استباقي: رصد فيروس محتمل", "الحالة": "جديد"}
    ]

# حالة للتحقق من الضغط على زر الإنذار
if "alert_acknowledged" not in st.session_state:
    st.session_state.alert_acknowledged = False

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

# --- تبويبات النظام الرئيسية ---
tab_titles = ["شاشة الموظفين والتنبيهات", "بوابة الإدارة والتقنية (IT)"] if lang == "العربية (AR)" else ["Employee Alerts", "Management & IT Portal"]
tab1, tab2 = st.tabs(tab_titles)

with tab1:
    st.subheader("شاشة التنبيهات الاستباقية للموظف" if lang == "العربية (AR)" else "Employee Proactive Alert Screen")
    
    # رسالة الإنذار الاستباقي الفوري مع زر OK
    if not st.session_state.alert_acknowledged:
        st.error("تنبيه: يتواجد برنامج ضار في الجهاز أو الهارد ديسك لا يعمل بشكل سليم (DEV-305). يرجى تأكيد الإرسال لقسم تقنية المعلومات.")
        
        if st.button("OK - إرسال التذكرة تلقائياً إلى الـ IT" if lang == "العربية (AR)" else "OK - Send Ticket Automatically to IT"):
            auto_ticket = {
                "رقم التذكرة": f"TICK-{len(st.session_state.tickets) + 101}",
                "الجهاز": "DEV-305",
                "القسم المستهدف": "قسم الدعم الفني",
                "الوصف": "إنذار استباقي: مشكلة بالهارد ديسك / عطل معالجة",
                "الحالة": "جديد (New)"
            }
            st.session_state.tickets.append(auto_ticket)
            st.session_state.alert_acknowledged = True
            st.rerun()
    else:
        st.success("تم تأكيد الإنذار وإرسال التذكرة بنجاح إلى قسم تقنية المعلومات. شكراً لتعاونك." if lang == "العربية (AR)" else "Alert acknowledged and ticket sent to IT successfully.")
        
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

    # بوابة تقنية المعلومات (IT) - مقسمة حسب الأقسام الرسمية
    elif "قسم تقنية المعلومات" in portal_choice or "IT Department" in portal_choice:
        it_passcode = st.text_input("أدخل كود الـ IT:" if lang == "العربية (AR)" else "Enter IT Password:", type="password", key="it_pass")
        if it_passcode == "it123":
            
            if lang == "العربية (AR)":
                sub_tabs = [
                    "إدارة الصحة الإلكترونية (E-health management)",
                    "قسم الأنظمة والتطبيقات (Systems and Applications)",
                    "قسم الدعم الفني (Technical Support)",
                    "قسم البنية التحتية (Infrastructure)"
                ]
            else:
                sub_tabs = [
                    "E-health management",
                    "Systems and Applications",
                    "Technical Support",
                    "Infrastructure"
                ]
                
            sub_tab = st.selectbox("اختر القسم:" if lang == "العربية (AR)" else "Select Department:", sub_tabs)
            
            # 1. إدارة الصحة الإلكترونية (ويتبع لها قسم الجودة)
            if "E-health" in sub_tab or "الصحة الإلكترونية" in sub_tab:
                st.markdown("### إدارة الصحة الإلكترونية (E-Health Management)")
                st.info("مراقبة التكامل الرقمي، جاهزية منصات الصحة الرقمية، ومؤشرات الأداء الإلكتروني.")
                
                quality_view = st.radio("اختر الوحدة التنظيمية:" if lang == "العربية (AR)" else "Select Unit:", 
                                        ["مؤشرات الصحة الإلكترونية العامّة", "وحدة الجودة (Quality Management Unit)"])
                
                if "وحدة الجودة" in quality_view or "Quality Management" in quality_view:
                    st.markdown("---")
                    st.markdown("#### لوحة قرارات مدير قسم الجودة (Quality & Compliance Decision Hub)")
                    st.success("يتخذ مدير الجودة هنا قرارات مراجعة مستويات الخدمة (SLA)، تقييم رضا المستفيدين، واعتماد معايير الأمان الرقمي.")
                    
                    quality_decision = st.selectbox("اتخاذ قرار إداري / اعتمادي:" if lang == "العربية (AR)" else "Make Quality Decision:", [
                        "اعتماد تقرير مطابقة الأداء الرقمي لشهر أغسطس",
                        "طلب خطة تحسين عاجلة لبطء استجابة الأنظمة الطبية",
                        "فتح مراجعة لالتزام فريق الدعم بأوقات معالجة البلاغات (SLA)"
                    ])
                    
                    if st.button("تنفيذ واعتماد القرار الإداري" if lang == "العربية (AR)" else "Execute Decision"):
                        st.info(f"تم اعتماد القرار بنجاح وتسجيله في سجل جودة الصحة الإلكترونية: ({quality_decision})")
                else:
                    st.bar_chart(pd.DataFrame({'معدل التكامل الرقمي %': [99.2, 98.5, 99.8, 99.5]}, index=["الربط المركزي", "السجلات الصحية", "الخدمات الإكلينيكية", "التكامل الإحصائي"]))

            # 2. قسم الأنظمة والتطبيقات
            elif "Systems" in sub_tab or "الأنظمة والتطبيقات" in sub_tab:
                st.markdown("### قسم الأنظمة والتطبيقات (Systems and Applications Department)")
                st.info("مراقبة استقرار بوابات الربط (APIs)، وتتبع التذاكر البرمجية وحالة تراخيص الأنظمة لضمان عدم توقف الخدمات.")
                
                app_status_df = pd.DataFrame({
                    "النظام / التطبيق": ["النظام الطبي (+Oasis)", "نظام إدارة المواعيد", "نظام المختبر والاشعة LIS/PACS"],
                    "حالة الاتصال والخدمة": ["متصل ومستقر", "مستقر", "تحذير: بطء طفيف بالاستجابة"],
                    "الشركة الموردة": ["شركة الحلول الطبية", "شركة التقنية الرقمية", "الأنظمة المتقدمة"]
                })
                st.table(app_status_df)
                st.success("القرار الاستباقي: تم رصد كفاءة عمل بوابات الربط وتوجيه الموردين بحل مشكلة البطء قبل توقف الخدمات.")

            # 3. قسم الدعم الفني
            elif "Technical Support" in sub_tab or "الدعم الفني" in sub_tab:
                st.markdown("### قسم الدعم الفني (Technical Support Department)")
                st.info("استقبال البلاغات الآلية الواردة فوراً من الأجهزة وإدارتها.")
                
                contractor = st.text_input("أدخل اسم الشركة المقاولة للصيانة (ثم اضغط Enter):" if lang == "العربية (AR)" else "Enter Maintenance Contractor Name:")
                
                if contractor:
                    st.success(f"تم ربط التذاكر الواردة وإرسالها تلقائياً إلى شركة الصيانة: {contractor}")
                
                st.markdown("#### سجل البلاغات الواردة آلياً من الأجهزة:")
                tickets_df = pd.DataFrame(st.session_state.tickets)
                if contractor:
                    tickets_df["الشركة المقاولة"] = contractor
                st.table(tickets_df)

            # 4. قسم البنية التحتية
            elif "Infrastructure" in sub_tab or "البنية التحتية" in sub_tab:
                st.markdown("### قسم البنية التحتية (Infrastructure Department)")
                st.info("مراقبة السيرفرات، غرف الاتصالات، ومعدل استهلاك النطاق الترددي للشبكة استباقياً.")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### جاهزية سيرفرات الداتا سنتر")
                    st.bar_chart(pd.DataFrame({'الجاهزية %': [99.5, 98.9, 99.8]}, index=["سيرفر أ", "سيرفر ب", "سيرفر ج"]))
                with col2:
                    st.markdown("#### أحمال استهلاك الشبكة (Mbps)")
                    st.line_chart(pd.DataFrame({"الاستهلاك": [45, 75, 90, 60, 40]}, index=["الصباح", "الظهر", "الذروة", "المساء", "الليل"]))
                
                st.warning("تنبيه استباقي: تم رصد ضغط عالي على سويتش مبنى العيادات، وتم تفعيل إعادة توزيع الأحمال آلياً.")
