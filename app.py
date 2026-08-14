import streamlit as st
import pandas as pd

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(
    page_title="VisiPulse - Health Cluster Proactive System",
    layout="wide"
)

# --- الترويسة العليا مع عرض الشعار وترجمة اللغات ---
header_col1, header_col2, header_col3 = st.columns([1.5, 3.5, 1])

with header_col1:
    sub_col_logo, sub_col_text = st.columns([1, 2])
    with sub_col_logo:
        try:
            st.image("logo.jpeg", width=65)
        except:
            st.write("VisiPulse")
    with sub_col_text:
        st.markdown("### **VisiPulse**")
        st.caption("طبقة الذكاء الاستباقي" if "lang" not in locals() or lang == "العربية (AR)" else "Proactive Intelligence Layer")

with header_col2:
    # سيتم تحديث عنوان النظام بناءً على اللغة المختار أدناه
    pass

with header_col3:
    lang = st.selectbox("Language / اللغة", ["العربية (AR)", "English (EN)"])

st.markdown("---")

# تفعيل الترجمة لعنوان النظام الرئيسي
if lang == "العربية (AR)":
    header_col2.markdown("<h2 style='text-align: center; color: #1a5276;'>نظام مراقبة البنية التحتية والإنذار المبكر</h2>", unsafe_allow_html=True)
    tab1_title = "شاشة الموظفين والتنبيهات"
    tab2_title = "بوابة الدخول الخاصة (IT & الإدارة العليا)"
else:
    header_col2.markdown("<h2 style='text-align: center; color: #1a5276;'>Infrastructure Monitoring & Early Warning System</h2>", unsafe_allow_html=True)
    tab1_title = "Employee Screen & Alerts"
    tab2_title = "Secure Login Portal (IT & Upper Management)"

# تبويبات النظام الرئيسية مع دعم اللغتين
tab1, tab2 = st.tabs([tab1_title, tab2_title])

with tab1:
    if lang == "العربية (AR)":
        st.subheader("شاشة التنبيهات الاستباقية للموظف")
        st.markdown("عند استباق النظام للعطل قبل وقوعه، تظهر نافذة التنبيه الذكية (Toast Notification) للموظف على جهازه:")
        st.warning("تنبيه استباقي (VisiPulse): تم رصد مؤشرات تراجع في أداء الجهاز المادي (DEV-101). النظام يعالج المشكلة استباقياً لتجنب التوقف.")
        if st.button("ضغط (OK) لتأكيد القراءة"):
            st.success("تم تأكيد الاستلام بنجاح، ومنع تكدس البلاغات العشوائية على قسم الدعم الفني.")
    else:
        st.subheader("Employee Proactive Alert Screen")
        st.markdown("When the system anticipates a failure before it occurs, a smart alert notification appears on the employee's device:")
        st.warning("Proactive Alert (VisiPulse): Performance degradation detected in hardware device (DEV-101). The system is addressing it proactively to prevent downtime.")
        if st.button("Click (OK) to Confirm Reading"):
            st.success("Acknowledgment confirmed successfully, preventing random ticket congestion on IT support.")

with tab2:
    if lang == "العربية (AR)":
        st.subheader("بوابات الدخول الآمنة للأقسام والإدارة")
        portal_choice = st.radio("اختر البوابة المطلوبة:", ["قسم تقنية المعلومات (IT Sub-divisions)", "الإدارة العليا (Upper Management)"])
        
        if portal_choice == "قسم تقنية المعلومات (IT Sub-divisions)":
            st.markdown("---")
            it_passcode = st.text_input("أدخل الكود السري الخاص بقسم الـ IT:", type="password", key="it_pass")
            
            if it_passcode == "it123":
                st.success("تم التحقق بنجاح. مرحباً بك في لوحة تحكم أقسام الصحة الإلكترونية وتقنية المعلومات:")
                
                it_sub_tab = st.selectbox("اختر القسم الفرعي المرتبط بالمنظومة:", [
                    "مدير الصحة الإلكترونية (e-Health)",
                    "قسم الدعم الفني (IT Support)",
                    "قسم الأنظمة الطبية (Medical System)",
                    "قسم الشبكات (Network)",
                    "قسم الجودة (Quality)"
                ])
                
                if it_sub_tab == "مدير الصحة الإلكترونية (e-Health)":
                    st.markdown("### لوحة مراقبة الصحة الإلكترونية (e-Health)")
                    st.info("آلية الاستفادة الاستباقية: مراقبة التوافق الرقمي وتكامل الأنظمة المساندة وضمان استمرارية الخدمات.")
                    st.success("القيمة المضافة: رفع كفاءة البنية الرقمية وتقليل مخاطر توقف الأنظمة.")
                    st.write("تربط هذه اللوحة كافة الأقسام التشغيلية لتوفير رؤية متكاملة لمدير الصحة الإلكترونية بمعزل تام عن قاعدة بيانات Oasis+.")

                elif it_sub_tab == "قسم الدعم الفني (IT Support)":
                    st.markdown("### لوحة تحكم قسم الدعم الفني والشركة المقاولة")
                    st.info("آلية الاستفادة الاستباقية: تتبع دورة حياة الأجهزة والتنبؤ بالأعطال قبل وقوعها.")
                    st.success("القيمة المضافة: خفض تكاليف الصيانة الاستباقية وزيادة عمر الأجهزة.")
                    
                    contractor_company = st.text_input("اسم الشركة المقاولة المسؤولة عن الصيانة:", placeholder="اكتب اسم الشركة هنا ثم اضغط إرسال أو Enter...", key="contractor_input")
                    if st.button("إرسال البلاغ تلقائياً للشركة المقاولة") or contractor_company:
                        if contractor_company:
                            st.success(f"تم إرسال البلاغ الاستباقي تلقائياً إلى شركة الصيانة: {contractor_company} مع تفاصيل العطل وتاريخ الجهاز.")
                        else:
                            st.info("الرجاء كتابة اسم الشركة المقاولة لتوجيه البلاغ.")

                elif it_sub_tab == "قسم الأنظمة الطبية (Medical System)":
                    st.markdown("### لوحة الأنظمة الطبية (Medical Systems)")
                    st.info("آلية الاستفادة الاستباقية: مراقبة مساحات تخزين السيرفرات وسرعة استجابة النظام الطبي دون إبطائه.")
                    st.success("القيمة المضافة: ضمان استقرار بيئة العمل الطبية وتدفق العمليات الإكلينيكية بسلاسة.")

                elif it_sub_tab == "قسم الشبكات (Network)":
                    st.markdown("### لوحة مراقبة الشبكات (Network)")
                    st.info("آلية الاستفادة الاستباقية: تحليل أوقات الذروة واستهلاك النطاق الترددي لتوزيع الأحمال استباقياً.")
                    st.success("القيمة المضافة: تحسين تجربة المستخدم وتقليل الاختناقات الرقمية.")

                elif it_sub_tab == "قسم الجودة (Quality)":
                    st.markdown("### لوحة جودة البيانات وحوكمتها (Quality)")
                    st.info("آلية الاستفادة الاستباقية: مراقبة أزمنة الاستجابة لحظياً وإطلاق علامات حمراء عند تجاوز المستهدفات.")
                    st.success("القيمة المضافة: ضمان الامتثال للمعايير وتحسين جودة الخدمة المقدمة للمرضى.")
                    
            elif it_passcode:
                st.error("الكود السري غير صحيح.")
            else:
                st.info("الرجاء إدخال الكود السري المخصص للـ IT للوصول للأقسام الفرعية.")

        elif portal_choice == "الإدارة العليا (Upper Management)":
            st.markdown("---")
            mgmt_passcode = st.text_input("أدخل الكود السري الخاص بالإدارة العليا:", type="password", key="mgmt_pass")
            
            if mgmt_passcode == "mgmt999":
                st.success("أهلاً بك في لوحة مؤشرات الإدارة العليا:")
                st.info("آلية الاستفادة الاستباقية: لوحات تحكم (Dashboards) ملخصة للمؤشرات الاستراتيجية وأداء المستشفى العام.")
                st.success("القيمة المضافة: دعم اتخاذ القرار المبني على الحقائق، وتقليل الفاقد التشغيلي.")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(label="إجمالي الكفاءة التشغيلية للمستشفى", value="94.8%", delta="+3.2% استباقي")
                with col_m2:
                    st.metric(label="الأعطال المتوقعة التي تم تفاديها", value="28 عطل")
            elif mgmt_passcode:
                st.error("الكود السري للإدارة غير صحيح.")
            else:
                st.info("الرجاء إدخال الكود السري الخاص بالإدارة العليا.")
    else:
        st.subheader("Secure Portals for Departments & Management")
        portal_choice = st.radio("Choose Required Portal:", ["IT Sub-divisions", "Upper Management"])
        
        if portal_choice == "IT Sub-divisions":
            st.markdown("---")
            it_passcode = st.text_input("Enter IT Passcode:", type="password", key="it_pass_en")
            
            if it_passcode == "it123":
                st.success("Verification successful. Welcome to IT & e-Health dashboard:")
                
                it_sub_tab = st.selectbox("Select Sub-division:", [
                    "e-Health Manager",
                    "IT Support",
                    "Medical Systems",
                    "Network",
                    "Quality"
                ])
                
                if it_sub_tab == "e-Health Manager":
                    st.markdown("### e-Health Monitoring Dashboard")
                    st.info("Proactive Value: Monitoring digital compatibility and ensuring service continuity.")
                    st.success("Added Value: Enhancing digital infrastructure efficiency and reducing outage risks.")
                    st.write("Connects operational departments to provide a comprehensive view for the e-Health manager completely independent of Oasis+ database.")

                elif it_sub_tab == "IT Support":
                    st.markdown("### IT Support & Contractor Dashboard")
                    st.info("Proactive Value: Tracking device lifecycle and predicting failures.")
                    st.success("Added Value: Lowering proactive maintenance costs and extending device lifespan.")
                    
                    contractor_company = st.text_input("Responsible Maintenance Contractor Company:", placeholder="Type company name here...", key="contractor_input_en")
                    if st.button("Send Ticket Automatically to Contractor") or contractor_company:
                        if contractor_company:
                            st.success(f"Proactive ticket automatically sent to contractor: {contractor_company} with device failure details.")
                        else:
                            st.info("Please enter the contractor company name.")

                elif it_sub_tab == "Medical Systems":
                    st.markdown("### Medical Systems Dashboard")
                    st.info("Proactive Value: Monitoring server storage and medical system response speed.")
                    st.success("Added Value: Ensuring stability of clinical environment and smooth workflow.")

                elif it_sub_tab == "Network":
                    st.markdown("### Network Monitoring Dashboard")
                    st.info("Proactive Value: Analyzing peak hours and bandwidth consumption.")
                    st.success("Added Value: Improving user experience and reducing digital bottlenecks.")

                elif it_sub_tab == "Quality":
                    st.markdown("### Data Quality & Governance Dashboard")
                    st.info("Proactive Value: Real-time tracking of response times and triggering alerts.")
                    st.success("Added Value: Ensuring standards compliance and improving service quality.")
                    
            elif it_passcode:
                st.error("Incorrect Passcode.")
            else:
                st.info("Please enter the IT passcode to access sub-divisions.")

        elif portal_choice == "Upper Management":
            st.markdown("---")
            mgmt_passcode = st.text_input("Enter Upper Management Passcode:", type="password", key="mgmt_pass_en")
            
            if mgmt_passcode == "mgmt999":
                st.success("Welcome to Upper Management Indicators Dashboard:")
                st.info("Proactive Value: Summarized dashboards for strategic indicators and general hospital performance.")
                st.success("Added Value: Fact-based decision making and reducing operational waste.")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(label="Total Hospital Operational Efficiency", value="94.8%", delta="+3.2% proactive")
                with col_m2:
                    st.metric(label="Anticipated Failures Prevented", value="28 Failures")
            elif mgmt_passcode:
                st.error("Incorrect Management Passcode.")
            else:
                st.info("Please enter the Upper Management passcode.")