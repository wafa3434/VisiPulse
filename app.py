import streamlit as st
import pandas as pd
import random

# إعداد الصفحة وتكوين النظام المعتمد
st.set_page_config(
    page_title="VisiPulse - E-Health Proactive Monitoring System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة الذاكرة المؤقتة للبلاغات والأجهزة
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {"القسم المسؤول": "قسم البنية التحتية", "اسم الجهاز": "SERVER-EX-01", "الموقع": "الداتا سنتر - الدور الأرضي", "نوع التنبيه": "تقني", "الحالة": "مغلقة"},
        {"القسم المسؤول": "قسم الأنظمة والتطبيقات", "اسم الجهاز": "SYS-MED-04", "الموقع": "طوارئ الأطفال", "نوع التنبيه": "تقني", "الحالة": "مغلقة"},
        {"القسم المسؤول": "قسم الدعم الفني", "اسم الجهاز": "PRN-PHARM-02", "الموقع": "صيدلية التنويم", "نوع التنبيه": "مادي (هاردوير)", "الحالة": "مغلقة"}
    ]

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
# 3. شاشة قسم الـ IT (قائمة منسدلة للأقسام الفرعية والمهام الاستباقية)
# ---------------------------------------------------------------------------
with main_tab3:
    st.subheader("بوابة إدارة الـ IT والأقسام التخصصية")
    
    it_sub_section = st.selectbox(
        "اختر القسم التخصصي:",
        [
            "اختر القسم...",
            "موظف الدعم الفني",
            "موظف الأنظمة والتطبيقات",
            "موظف البنية التحتية",
            "مدير الجودة",
            "مدير الصحة الإلكترونية"
        ]
    )
    
    # 3.1. موظف الدعم الفني (يتضمن الرسم البياني وإحصائيات وتحميل ملف الأجهزة)
    if it_sub_section == "موظف الدعم الفني":
        st.write("### واجهة موظف الدعم الفني وإحصائيات الأجهزة")
        sup_pass = st.text_input("أدخل رمز الدخول لقسم الدعم الفني:", type="password", key="pass_sup")
        if sup_pass == "sup123":
            st.success("تم الدخول لواجهة الدعم الفني بنجاح.")
            
            st.write("المهام والاستجابة لبلاغات الهاردوير والأجهزة الطرفية:")
            support_tickets = [t for t in st.session_state.tickets if t["القسم المسؤول"] == "قسم الدعم الفني"]
            if support_tickets:
                st.table(pd.DataFrame(support_tickets))
            else:
                st.info("لا توجد بلاغات معلقة للدعم الفني حالياً.")
                
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
        elif sup_pass:
            st.warning("رمز الدخول غير صحيح.")

    # 3.2. موظف الأنظمة والتطبيقات
    elif it_sub_section == "موظف الأنظمة والتطبيقات":
        st.write("### واجهة موظف الأنظمة والتطبيقات")
        sys_pass = st.text_input("أدخل رمز الدخول لقسم الأنظمة والتطبيقات:", type="password", key="pass_sys")
        if sys_pass == "sys123":
            st.success("تم الدخول لواجهة الأنظمة والتطبيقات بنجاح.")
            st.metric("مراقبة استقرار الروابط (Link Stability)", "99.2%", "مستقر بدون تذبذب حرج")
            st.write("المهام الاستباقية: مراقبة مستمرة للروابط والتأكد من عدم وجود أي تذبذب بين التطبيقات وقواعد البيانات.")
            
            sys_tickets = [t for t in st.session_state.tickets if t["القسم المسؤول"] == "قسم الأنظمة والتطبيقات"]
            if sys_tickets:
                st.table(pd.DataFrame(sys_tickets))
            else:
                st.info("لا توجد بلاغات معلقة للأنظمة والتطبيقات.")
        elif sys_pass:
            st.warning("رمز الدخول غير صحيح.")

    # 3.3. موظف البنية التحتية
    elif it_sub_section == "موظف البنية التحتية":
        st.write("### واجهة موظف البنية التحتية")
        inf_pass = st.text_input("أدخل رمز الدخول لقسم البنية التحتية:", type="password", key="pass_inf")
        if inf_pass == "infra123":
            st.success("تم الدخول لواجهة البنية التحتية بنجاح.")
            
            c_inf1, c_inf2, c_inf3 = st.columns(3)
            c_inf1.metric("جاهزية الداتا سنتر", "99.99%", "ممتاز")
            c_inf2.metric("أحمال الشبكة والسويتشات", "67.3%", "مستقر وآمن")
            c_inf3.metric("حرارة معالجات السيرفرات (CPU)", "41.2 C", "ضمن المعتاد")
            
            st.warning("التنبيه الاستباقي للبنية التحتية: رصد مستمر لأحمال السويتشات ودرجات حرارة المعالجات لتفادي أي اختناق في البيانات.")
            
            infra_tickets = [t for t in st.session_state.tickets if t["القسم المسؤول"] == "قسم البنية التحتية"]
            if infra_tickets:
                st.table(pd.DataFrame(infra_tickets))
            else:
                st.info("لا توجد بلاغات معلقة للبنية التحتية.")
        elif inf_pass:
            st.warning("رمز الدخول غير صحيح.")

    # 3.4. مدير الجودة
    elif it_sub_section == "مدير الجودة":
        st.write("### واجهة مدير الجودة")
        q_pass = st.text_input("أدخل رمز الدخول لقسم الجودة:", type="password", key="pass_q")
        if q_pass == "quality2026":
            st.success("تم الدخول لواجهة إدارة الجودة بنجاح.")
            st.metric("معدل امتثال المعايير التقنية والصحية", "99.3%", "مستقر")
            st.info("المهام الاستباقية: رصد الفجوات في مؤشرات الأداء التقني ومعايير الاعتماد المؤسسي واتخاذ التدابير التصحيحية.")
        elif q_pass:
            st.warning("رمز الدخول غير صحيح.")

    # 3.5. مدير الصحة الإلكترونية
    elif it_sub_section == "مدير الصحة الإلكترونية":
        st.write("### واجهة إدارة الصحة الإلكترونية")
        ehealth_pass = st.text_input("أدخل رمز الدخول لإدارة الصحة الإلكترونية:", type="password", key="pass_eh")
        if ehealth_pass == "mgmt999":
            st.success("تم الدخول لواجهة إدارة الصحة الإلكترونية بنجاح.")
            st.metric("كفاءة التكامل الشامل للأنظمة الطبية", "99.1%", "عالي")
            st.info("المهام: الإشراف العام على الأقسام المندرجة وتحليل تقارير الأداء الشاملة لصناع القرار.")
        elif ehealth_pass:
            st.warning("رمز الدخول غير صحيح.")
