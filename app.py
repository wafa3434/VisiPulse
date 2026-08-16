import streamlit as st
import pandas as pd
import random

# إعداد الصفحة وتكوين النظام المعتمد
st.set_page_config(
    page_title="VisiPulse - E-Health Proactive Monitoring System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة الذاكرة المؤقتة للبلاغات في النظام
if "tickets" not in st.session_state:
    st.session_state.tickets = []

# دالة توليد التنبيهات الاستباقية الواقعية للأقسام
def get_proactive_alert():
    departments_data = [
        {
            "dept": "قسم الأنظمة والتطبيقات", 
            "issue": "رصد تذبذب غير مستقرار في الروابط (Link Jitter) بين واجهة التطبيق وقاعدة البيانات الطبية"
        },
        {
            "dept": "قسم البنية التحتية", 
            "issue": "تنبيه استباقي: ارتفاع أحمال السويتشات الرئيسية واقتراب حرارة معالجات السيرفرات من الحد الحراري الأقصى"
        },
        {
            "dept": "قسم الدعم الفني", 
            "issue": "تراكم استباقي لبلاغات بطء أجهزة صرف الأدوية الطرفية في الوحدات السريرية"
        },
        {
            "dept": "إدارة الصحة الإلكترونية والجودة", 
            "issue": "رصد فجوات محتملة في مؤشرات الأداء التقني (KPIs) ومعايير الاعتماد المؤسسي"
        }
    ]
    selected = random.choice(departments_data)
    return {
        "department": selected["dept"],
        "detected_issue": selected["issue"],
        "device_id": f"THC-HOSP-SYS-{random.randint(1000,9999)}"
    }

if "current_alert" not in st.session_state:
    st.session_state.current_alert = get_proactive_alert()

# وظيفة تصدير التقارير الرسمية المعتمدة
def generate_stats_csv():
    if not st.session_state.tickets:
        return ""
    df = pd.DataFrame(st.session_state.tickets)
    return df.to_csv(index=False).encode('utf-8-sig')

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

# ==================== القائمة الرئيسية (التبويبات المعتمدة) ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "شاشة الموظفين (المراقبة الفورية)", 
    "إدارة الصحة الإلكترونية وقسم الجودة", 
    "قسم البنية التحتية", 
    "قسم الأنظمة والدعم الفني"
])

# 1. شاشة الموظفين والعمليات الحية
with tab1:
    st.subheader("لوحة التنبيهات الاستباقية المباشرة")
    alert = st.session_state.current_alert
    
    st.error(f"تنبيه استباقي موجه إلى [{alert['department']}]: {alert['detected_issue']}")
    
    with st.form("employee_action_form"):
        st.write("معرّف الأصول / السيرفر:", alert["device_id"])
        st.write("طبيعة الحدث المرصود:", alert["detected_issue"])
        
        action_note = st.text_input("تسجيل ملاحظات التعامل الأولي الميداني:")
        submitted = st.form_submit_button("اعتماد وتصعيد البلاغ الاستباقي إلى قسم الاختصاص")
        
        if submitted:
            new_ticket = {
                "القسم المسؤول": alert["department"],
                "المعرف التقني": alert["device_id"],
                "وصف المشكلة الاستباقية": alert["detected_issue"],
                "ملاحظات الموظف": action_note if action_note else "لا توجد ملاحظات",
                "الحالة": "قيد المعالجة الاستباقية"
            }
            st.session_state.tickets.append(new_ticket)
            st.success("تم إرسال البلاغ وتوثيقه في السجل المركزى بنجاح.")
            st.session_state.current_alert = get_proactive_alert()
            st.rerun()

# 2. إدارة الصحة الإلكترونية وقسم الجودة (صناع القرار والرسومات البيانية)
with tab2:
    st.subheader("لوحة تحكم إدارة الصحة الإلكترونية واتخاذ القرار (مدمج معها قسم الجودة)")
    
    quality_pass = st.text_input("أدخل كود اعتماد صلاحيات الإدارة العليا والجودة:", type="password", key="quality_login")
    
    if quality_pass == "quality2026" or quality_pass == "mgmt999":
        st.success("تم اعتماد الصلاحية بنجاح. عرض المؤشرات والرسومات التحليلية الاستراتيجية:")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("مؤشر استقرار البنية والروابط", "98.7%", "+0.4%")
        kpi2.metric("الأعطال المتلافة استباقياً", str(len(st.session_state.tickets) + 19), "+5")
        kpi3.metric("معدل امتثال معايير الجودة التقنية", "99.2%", "مستقر")
        kpi4.metric("إجمالي البلاغات النشطة", len(st.session_state.tickets), "متابعة")
        
        st.markdown("---")
        st.write("### التحليلات الرسومية لدعم اتخاذ القرار الاستراتيجي")
        
        chart_data = pd.DataFrame({
            'التخصص التقني': ['البنية التحتية', 'الأنظمة والتطبيقات', 'الدعم الفني', 'إدارة الجودة'],
            'كفاءة التشغيل (%)': [98, 95, 97, 99],
            'عدد التنبيهات المعالجة': [12, 18, 25, 8]
        })
        
        st.bar_chart(chart_data.set_index('التخصص التقني'))
        
        st.info("تتيح هذه المؤشرات لصناع القرار في إدارة الصحة الإلكترونية والجودة اعتماد خطط التطوير الفوري وتوجيه فرق الصيانة قبل تفاقم أي انحراف تشغيلي.")
        
    elif quality_pass:
        st.warning("رمز الصلاحية غير صحيح. يرجى مراجعة إدارة النظام.")
    else:
        st.info("يرجى إدخال رمز المرور الخاص بإدارة الصحة الإلكترونية وقسم الجودة لعرض لوحات التحكم والرسومات البيانية.")

# 3. قسم البنية التحتية (جاهزية الداتا سنتر، أحمال الشبكة، وحرارة المعالجات)
with tab3:
    st.subheader("قسم البنية التحتية - مراقبة الداتا سنتر والحرارة والأحمال")
    
    infra_pass = st.text_input("أدخل كود صلاحيات قسم البنية التحتية:", type="password", key="infra_login")
    
    if infra_pass == "infra123":
        st.success("تم تفعيل واجهة مراقبة البنية التحتية والبيانات الحية:")
        
        col_inf1, col_inf2, col_inf3 = st.columns(3)
        col_inf1.metric("حرارة معالجات السيرفرات (CPU)", "41.5 C", "طبيعي مستقر")
        col_inf2.metric("أحمال السويتشات الرئيسية (Throughput)", "68.4%", "ضمن الآمن")
        col_inf3.metric("جاهزية واستمرارية الداتا سنتر", "99.99%", "ممتاز")
        
        st.markdown("---")
        st.write("#### المهام الاستباقية المرصودة في البنية التحتية:")
        st.warning("تنبيه استباقي: يتم فحص وحدات التبريد ومراقبة أي ضغط استثنائي محتمل على السويتشات المركزية قبل حدوث أي اختناق في حركة البيانات.")
        
        if st.session_state.tickets:
            infra_tickets = [t for t in st.session_state.tickets if "البنية التحتية" in t["القسم المسؤول"]]
            if infra_tickets:
                st.write("البلاغات الخاصة بالبنية التحتية:")
                st.table(pd.DataFrame(infra_tickets))
            else:
                st.info("لا توجد بلاغات عاجلة مسجلة على البنية التحتية حالياً.")
        
    elif infra_pass:
        st.warning("رمز الدخول لقسم البنية التحتية غير صحيح.")
    else:
        st.info("يرجى إدخال رمز المرور الخاص بفريق البنية التحتية للاطلاع على قراءات الداتا سنتر وأحمال الشبكة.")

# 4. قسم الأنظمة والتطبيقات والدعم الفني (استقرار الروابط والتذبذب)
with tab4:
    st.subheader("قسم الأنظمة والتطبيقات ودعم الروابط")
    
    sys_pass = st.text_input("أدخل كود صلاحيات قسم الأنظمة والتطبيقات:", type="password", key="sys_login")
    
    if sys_pass == "sys123":
        st.success("تم تفعيل واجهة مراقبة الروابط والتطبيقات الحية:")
        
        s_col1, s_col2 = st.columns(2)
        s_col1.metric("استقرار روابط الاتصال بالأنظمة الطبية", "99.4%", "مستقر (بدون تذبذب حرج)")
        s_col2.metric("استجابة قواعد البيانات الاستعلامية", "14 ms", "أداء عالي")
        
        st.markdown("---")
        st.write("#### مراقبة التذبذب واستقرار الروابط (Link Jitter & Stability):")
        st.info("النظام يقوم بمراقبة مستمرة لتجنب أي تذبذب في الاتصال بين وحدات الأقسام الطبية وقواعد البيانات المركزية لتأمين استمرار تدفق البيانات الطبية بلا انقطاع.")
        
        if st.session_state.tickets:
            sys_tickets = [t for t in st.session_state.tickets if "الأنظمة والتطبيقات" in t["القسم المسؤول"] or "الدعم الفني" in t["القسم المسؤول"]]
            if sys_tickets:
                st.write("سجل التذاكر والبلاغات المعلقة للأنظمة والتطبيقات:")
                st.table(pd.DataFrame(sys_tickets))
                
                if st.button("تحديث وإغلاق البلاغات المعالجة في الأنظمة"):
                    st.session_state.tickets = [t for t in st.session_state.tickets if t not in sys_tickets]
                    st.success("تم إغلاق وتحديث البلاغات بنجاح.")
                    st.rerun()
            else:
                st.info("لا توجد بلاغات معلقة تخص الأنظمة والتطبيقات.")
                
        csv_data = generate_stats_csv()
        if csv_data:
            st.download_button("تصدير تقرير النظام الشامل (CSV)", data=csv_data, file_name="VisiPulse_Official_Report.csv", mime="text/csv")
            
    elif sys_pass:
        st.warning("رمز الدخول لقسم الأنظمة غير صحيح.")
    else:
        st.info("يرجى إدخال رمز المرور الخاص بقسم الأنظمة والتطبيقات لمتابعة حالة الروابط والتذبذب.")
