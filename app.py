
import streamlit as st
import pandas as pd
import random

# إعداد الصفحة وتكوين النظام المعتمد
st.set_page_config(
    page_title="VisiPulse - E-Health Proactive Monitoring System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة الذاكرة المؤقتة للبلاغات والقرارات
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {"القسم المسؤول": "قسم البنية التحتية", "اسم الجهاز": "SERVER-EX-01", "الموقع": "الداتا سنتر - الدور الأرضي", "نوع التنبيه": "تقني", "الحالة": "مغلقة"},
        {"القسم المسؤول": "قسم الأنظمة والتطبيقات", "اسم الجهاز": "SYS-MED-04", "الموقع": "طوارئ الأطفال", "نوع التنبيه": "تقني", "الحالة": "مغلقة"},
        {"القسم المسؤول": "قسم الدعم الفني", "اسم الجهاز": "PRN-PHARM-02", "الموقع": "صيدلية التنويم", "نوع التنبيه": "مادي (هاردوير)", "الحالة": "مغلقة"}
    ]

if "maintenance_dispatches" not in st.session_state:
    st.session_state.maintenance_dispatches = []

if "quality_decisions" not in st.session_state:
    st.session_state.quality_decisions = []

# دالة توليد التنبيهات الاستباقية للموظف
def get_employee_alert():
    devices = [
        {"name": "MONITOR-ICU-12", "location": "العناية المركزة للأطفال - السرير 4", "type": "تقني"},
        {"name": "PRINTER-ER-03", "location": "قسم الطوارئ - الاستقبال", "type": "مادي (هاردوير)"},
        {"name": "SERVER-LAB-01", "location": "المختبر الرئيسي - الرف الثاني", "type": "تقني"},
        {"name": "ACCESS-POINT-COR-05", "location": "ممر العيادات الخارجية - الطابق الأول", "type": "تقني"}
    ]
    selected_dev = random.choice(devices)
    issues = [
        "رصد بطء استجابة وتنبيه استباقي لاحتمالية توقف الخدمة مؤقتاً",
        "تذبذب في خط الاتصال الرئيسي المرتبط بقاعدة البيانات",
        "تنبيه استباقي: ارتفاع مؤشرات الاستهلاك واقتراب الحاجة للصيانة الوقائية"
    ]
    return {
        "device_name": selected_dev["name"],
        "location": selected_dev["location"],
        "alert_type": selected_dev["type"],
        "issue_desc": random.choice(issues)
    }

if "employee_current_alert" not in st.session_state:
    st.session_state.employee_current_alert = get_employee_alert()

# وظيفة تصدير تقارير إحصائيات الأجهزة وأكثر الأقسام عطلاً (Excel/CSV)
def generate_excel_stats():
    df_all = pd.DataFrame(st.session_state.tickets)
    if df_all.empty:
        df_all = pd.DataFrame(columns=["القسم المسؤول", "اسم الجهاز", "الموقع", "نوع التنبيه", "الحالة"])
    return df_all.to_csv(index=False).encode('utf-8-sig')

# ==================== الترويسة العلوية الرسمية ====================
header_col1, header_col2, header_col3 = st.columns([1, 6, 2])

with header_col1:
    try:
        st.image("logo.jpeg", width=110)
    except:
        st.markdown("**تجمع الطائف الصحي**")

with header_col2:
    st.markdown(
        "<h2 style='text-align: center; color: #1a5276; margin-bottom: 0;'>VisiPulse - نظام المراقبة الاستباقية لإدارة الصحة الإلكترونية</h2>"
        "<p style='text-align: center; color: #555; font-size: 14px;'>Predictive Hospital Monitor System - Taif Health Cluster</p>",
        unsafe_allow_html=True
    )

with header_col3:
    lang = st.selectbox("Language / لغة النظام", ["العربية", "English"])

st.markdown("---")

# ==================== القائمة الرئيسية للثلاث واجهات الكبرى ====================
main_tab1, main_tab2, main_tab3 = st.tabs([
    "شاشة الموظف (المراقبة الميدانية الفورية)", 
    "شاشة الإدارة العليا (المؤشرات والرسوم)", 
    "شاشة قسم الـ IT والأقسام التخصصية"
])

# ---------------------------------------------------------------------------
# 1. شاشة الموظف
# ---------------------------------------------------------------------------
with main_tab1:
    st.subheader("لوحة التنبيهات الاستباقية الفورية للموظف")
    
    current_al = st.session_state.employee_current_alert
    
    st.write("تفاصيل الجهاز المرصود تلقائياً في النظام:")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("اسم الجهاز", current_al["device_name"])
    col_b.metric("الموقع داخل المستشفى", current_al["location"])
    col_c.metric("نوع التنبيه", current_al["alert_type"])
    
    st.error(f"حالة الإنذار الاستباقي: {current_al['issue_desc']}")
    
    if st.button("موافق (OK) - إرسال البلاغ تلقائياً إلى قسم الـ IT المختص"):
        target_dept = "قسم الأنظمة والتطبيقات" if current_al["alert_type"] == "تقني" else "قسم الدعم الفني"
        new_ticket = {
            "القسم المسؤول": target_dept,
            "اسم الجهاز": current_al["device_name"],
            "الموقع": current_al["location"],
            "نوع التنبيه": current_al["alert_type"],
            "الحالة": "مفتوحة وعاجلة"
        }
        st.session_state.tickets.append(new_ticket)
        st.success("تم إرسال البلاغ بنجاح إلى قسم الـ IT المختص.")
        st.session_state.employee_current_alert = get_employee_alert()
        st.rerun()

# ---------------------------------------------------------------------------
# 2. شاشة الإدارة العليا
# ---------------------------------------------------------------------------
with main_tab2:
    st.subheader("لوحة مؤشرات الأداء الاستراتيجية والرسوم البيانية للإدارة العليا")
    
    admin_pass = st.text_input("أدخل رمز الدخول الخاص بالإدارة العليا:", type="password", key="admin_top_pass")
    
    if admin_pass == "mgmt999":
        st.success("تم التحقق من صلاحيات الإدارة العليا بنجاح.")
        
        kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
        kpi_1.metric("مؤشر استقرار البنية التحتية", "98.9%", "+0.5%")
        kpi_2.metric("إجمالي الأعطال المتلافة استباقياً", "142", "+12")
        kpi_3.metric("نسبة كفاءة التشغيل الطبي التقني", "99.4%", "مستقر")
        kpi_4.metric("إجمالي البلاغات المسجلة حالياً", len(st.session_state.tickets), "متابعة")
        
        st.markdown("---")
        st.write("الرسوم البيانية الاستراتيجية لكفاءة أقسام المستشفى:")
        
        strat_data = pd.DataFrame({
            'القسم': ['البنية التحتية', 'الأنظمة والتطبيقات', 'الدعم الفني', 'إدارة الجودة'],
            'معدل الاستجابة السريعة (%)': [99, 96, 98, 99.5]
        })
        st.bar_chart(strat_data.set_index('القسم'))
        
    elif admin_pass:
        st.warning("رمز الدخول غير صحيح.")
    else:
        st.info("يرجى إدخال كلمة المرور للاطلاع على مؤشرات الإدارة العليا.")

# ---------------------------------------------------------------------------
# 3. شاشة قسم الـ IT (رمز دخول موحد للـ IT بالكامل مع قائمة منسدلة)
# ---------------------------------------------------------------------------
with main_tab3:
    st.subheader("بوابة إدارة الـ IT والأقسام التخصصية")
    
    it_master_pass = st.text_input("أدخل رمز الدخول الموحد لقسم الـ IT (it2026):", type="password", key="it_general_pass")
    
    if it_master_pass == "it2026":
        st.success("تم التحقق من صلاحيات قسم الـ IT بنجاح.")
        
        it_sub_section = st.selectbox(
            "اختر القسم التخصصي:",
            [
                "موظف الدعم الفني",
                "موظف الأنظمة والتطبيقات",
                "موظف البنية التحتية",
                "مدير الجودة",
                "مدير الصحة الإلكترونية"
            ]
        )
        
        st.markdown("---")
        
        # 3.1. موظف الدعم الفني
        if it_sub_section == "موظف الدعم الفني":
            st.write("### واجهة موظف الدعم الفني وإحصائيات الأجهزة")
            st.write("المهام الاستباقية: معالجة بلاغات الأجهزة الطرفية ومراقبة وتتبع أعطال الهاردوير والإحصائيات الشهرية وملفات التصدير.")
            
            support_tickets = [t for t in st.session_state.tickets if t["القسم المسؤول"] == "قسم الدعم الفني"]
            if support_tickets:
                st.table(pd.DataFrame(support_tickets))
            else:
                st.info("لا توجد بلاغات معلقة للدعم الفني حالياً.")
                
            st.markdown("---")
            st.subheader("إرسال بلاغ عطل صياني إلى الشركة المقاولة مباشرة")
            
            with st.form("contractor_maintenance_form"):
                contractor_name = st.text_input("اسم الشركة المقاولة للتشغيل والصيانة:")
                fault_description = st.text_input("نوع العطل التفصيلي:")
                dispatch_submitted = st.form_submit_button("إرسال البلاغ فوراً إلى الشركة المقاولة (Enter)")
                
                if dispatch_submitted:
                    if contractor_name and fault_description:
                        new_dispatch = {
                            "الشركة المقاولة": contractor_name,
                            "نوع العطل": fault_description,
                            "حالة الإرسال": "تم الإرسال والربط بنجاح"
                        }
                        st.session_state.maintenance_dispatches.append(new_dispatch)
                        st.success(f"تم إرسال بلاغ العطل بنجاح إلى شركة [{contractor_name}] المقاولة.")
                    else:
                        st.warning("يرجى إدخال اسم الشركة المقاولة ونوع العطل بشكل صحيح.")
            
            if st.session_state.maintenance_dispatches:
                st.write("سجل بلاغات الصيانة المرسلة للشركات المقاولة:")
                st.table(pd.DataFrame(st.session_state.maintenance_dispatches))

            st.markdown("---")
            st.subheader("إحصائيات وتحليلات أعطال الأجهزة")
            
            monthly_data = pd.DataFrame({
                'الشهر': ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس'],
                'عدد البلاغات الاستباقية': [14, 19, 12, 22, 17, 25, 20, len(st.session_state.tickets) + 15]
            })
            st.bar_chart(monthly_data.set_index('الشهر'))
            
            st.write("سحب إحصائيات الأجهزة الشاملة لمعرفة أكثر الأقسام تعطلًا للأجهزة:")
            csv_file = generate_excel_stats()
            st.download_button(
                label="تحميل ملف إحصائيات الأجهزة (Excel/CSV)",
                data=csv_file,
                file_name="Hospital_Devices_Failure_Statistics.csv",
                mime="text/csv"
            )

        # 3.2. موظف الأنظمة والتطبيقات
        elif it_sub_section == "موظف الأنظمة والتطبيقات":
            st.write("### واجهة موظف الأنظمة والتطبيقات")
            st.metric("مراقبة استقرار الروابط (Link Stability)", "99.2%", "مستقر بدون تذبذب حرج")
            st.write("المهام الاستباقية: مراقبة مستمرة للروابط والتأكد من عدم وجود أي تذبذب بين التطبيقات وقواعد البيانات المركزية.")
            
            sys_tickets = [t for t in st.session_state.tickets if t["القسم المسؤول"] == "قسم الأنظمة والتطبيقات"]
            if sys_tickets:
                st.table(pd.DataFrame(sys_tickets))
            else:
                st.info("لا توجد بلاغات معلقة للأنظمة والتطبيقات.")

        # 3.3. موظف البنية التحتية
        elif it_sub_section == "موظف البنية التحتية":
            st.write("### واجهة موظف البنية التحتية")
            
            c_inf1, c_inf2, c_inf3 = st.columns(3)
            c_inf1.metric("جاهزية الداتا سنتر", "99.99%", "ممتاز")
            c_inf2.metric("أحمال الشبكة والسويتشات", "67.3%", "مستقر وآمن")
            c_inf3.metric("حرارة معالجات السيرفرات (CPU)", "41.2 C", "ضمن المعتاد")
            
            st.warning("المهام الاستباقية: رصد مستمر لأحمال السويتشات، درجات حرارة معالجات السيرفرات، وجاهزية الداتا سنتر لتفادي أي اختناق في البيانات.")
            
            st.markdown("---")
            st.subheader("الرسوم البيانية لأداء البنية التحتية والسيرفرات")
            
            infra_load_data = pd.DataFrame({
                'النطاق': ['السيرفرات الرئيسية', 'محولات الشبكة', 'أنظمة التبريد', 'قواعد البيانات'],
                'نسبة الاستهلاك أو الحمل (%)': [72, 65, 58, 80]
            })
            st.bar_chart(infra_load_data.set_index('النطاق'))
            
            infra_tickets = [t for t in st.session_state.tickets if t["القسم المسؤول"] == "قسم البنية التحتية"]
            if infra_tickets:
                st.table(pd.DataFrame(infra_tickets))
            else:
                st.info("لا توجد بلاغات معلقة للبنية التحتية.")

        # 3.4. مدير الجودة (مع الرسوم البيانية وخانة القرارات الإدارية)
        elif it_sub_section == "مدير الجودة":
            st.write("### واجهة مدير الجودة")
            st.metric("معدل امتثال المعايير التقنية والصحية", "99.3%", "مستقر")
            st.info("المهام الاستباقية: رصد الفجوات في مؤشرات الأداء التقني (KPIs) ومعايير الاعتماد المؤسسي واتخاذ التدابير التصحيحية.")
            
            st.markdown("---")
            st.subheader("الرسوم البيانية لمؤشرات أداء الجودة والامتثال")
            
            quality_chart_data = pd.DataFrame({
                'معيار الجودة': ['سلامة المرضى التقنية', 'سرعة إغلاق البلاغات', 'الامتثال للمعايير الأمنية', 'رضا المستفيدين الداخليين'],
                'نسبة الالتزام (%)': [99.5, 97.8, 98.9, 99.1]
            })
            st.bar_chart(quality_chart_data.set_index('معيار الجودة'))
            
            st.markdown("---")
            st.subheader("تدوين واقتراح القرارات الإدارية التصحيحية")
            
            with st.form("quality_decision_form"):
                decision_text = st.text_area("اكتب القرار الإداري المقترح أو التوصية التصحيحية:")
                decision_submitted = st.form_submit_button("حفظ وإرسال القرار الإداري")
                
                if decision_submitted:
                    if decision_text:
                        st.session_state.quality_decisions.append({"القرار الإداري": decision_text, "الحالة": "معتمد للتنفيذ"})
                        st.success("تم حفظ القرار الإداري المقترح بنجاح وإدراجه في السجل.")
                    else:
                        st.warning("يرجى كتابة نص القرار الإداري قبل الإرسال.")
            
            if st.session_state.quality_decisions:
                st.write("سجل القرارات الإدارية المقترحة من إدارة الجودة:")
                st.table(pd.DataFrame(st.session_state.quality_decisions))

        # 3.5. مدير الصحة الإلكترونية
        elif it_sub_section == "مدير الصحة الإلكترونية":
            st.write("### واجهة إدارة الصحة الإلكترونية")
            st.metric("كفاءة التكامل الشامل للأنظمة الطبية", "99.1%", "عالي")
            st.info("المهام الاستباقية: الإشراف العام على الأقسام المندرجة وتحليل تقارير الأداء الشاملة لصناع القرار.")
            
            st.markdown("---")
            st.subheader("الرسوم البيانية الشاملة لكفاءة التكامل الصحي التقني")
            
            ehealth_perf_data = pd.DataFrame({
                'النظام الطبي المدمج': ['الملف الطبي الإلكتروني', 'نظام التصوير الإشعاعي (PACS)', 'نظام المختبرات (LIS)', 'نظام المواعيد والطوارئ'],
                'معدل كفاءة التشغيل (%)': [99.5, 98.2, 99.0, 97.8]
            })
            st.bar_chart(ehealth_perf_data.set_index('النظام الطبي المدمج'))

    elif it_master_pass:
        st.warning("رمز الدخول لقسم الـ IT غير صحيح.")
    else:
        st.info("يرجى إدخال رمز الدخول الموحد الخاص بقسم الـ IT (it2026) للوصول إلى القائمة المنسدلة والأقسام التخصصية.")
