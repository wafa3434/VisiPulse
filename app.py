import streamlit as st
import pandas as pd
import random

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - E-Health Proactive Monitoring System", layout="wide")

# تهيئة الذاكرة للتذاكر
if "tickets" not in st.session_state:
    st.session_state.tickets = []

# دالة توليد تنبيهات استباقية لكل قسم
def get_proactive_alert():
    departments_data = [
        {"dept": "قسم الأنظمة والتطبيقات", "issue": "تعطل مفاجئ في النظام الطبي/قواعد البيانات"},
        {"dept": "قسم الدعم الفني", "issue": "تراكم بلاغات الهاردوير أو بطء استجابة الأجهزة"},
        {"dept": "قسم البنية التحتية", "issue": "انقطاع أو تلف نقطة الاتصال (Access Point)"},
        {"dept": "قسم الجودة", "issue": "رصد فجوات في مؤشرات الأداء التقني ومعايير الاعتماد"}
    ]
    
    selected = random.choice(departments_data)
    return {
        "department": selected["dept"],
        "detected_issue": selected["issue"],
        "device_name": f"THC-MONITOR-{random.randint(100,999)}"
    }

if "current_alert" not in st.session_state:
    st.session_state.current_alert = get_proactive_alert()

# وظيفة تصدير التقارير
def generate_stats_csv():
    if not st.session_state.tickets:
        return ""
    df = pd.DataFrame(st.session_state.tickets)
    return df.to_csv(index=False).encode('utf-8-sig')

# --- الجزء المحدث: عرض الشعار والترجمة ---
header_col1, header_col2, header_col3 = st.columns([1, 6, 2])

with header_col1:
    # عرض الشعار الخاص بك
    try:
        st.image("logo.jpeg", width=120)
    except:
        st.write("الشعار هنا")

with header_col2:
    st.markdown("<h3 style='text-align: center; color: #1a5276;'>VisiPulse - نظام المراقبة الاستباقية لإدارة الصحة الإلكترونية</h3>", unsafe_allow_html=True)

with header_col3:
    lang = st.selectbox("Language / اللغة", ["العربية", "English"])

st.markdown("---")

# --- شريط حالة المراقبة الحية ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("حالة نظام المراقبة", "متصل ويراقب", "Live")
m2.metric("الأجهزة المراقبة", "1,420 جهاز", "نشط")
m3.metric("الأنظمة الطبية المرصودة", "48 نظام", "100%")
m4.metric("التنبيهات الاستباقية المباشرة", len(st.session_state.tickets), "عاجل")

st.markdown("---")

# التبويبات الرئيسية
tab1, tab2, tab3 = st.tabs(["شاشة الموظفين (المراقبة الاستباقية)", "بوابة الإدارة العليا", "بوابة الأقسام (IT & Quality)"])

# 1. شاشة الموظفين
with tab1:
    st.subheader("لوحة التنبيهات الاستباقية الفورية")
    alert = st.session_state.current_alert
    
    st.error(f"تنبيه استباقي من نظام المراقبة في {alert['department']}: {alert['detected_issue']}")
    
    with st.form("proactive_alert_form"):
        st.write("القسم المستهدف:", alert["department"])
        st.write("المعرف المراقب:", alert["device_name"])
        st.write("تفاصيل الخلل المرصود:", alert["detected_issue"])
        
        is_hardware = ("البنية التحتية" in alert["department"] or "الدعم الفني" in alert["department"])
        maint_needed = "غير مطلوب"
        if is_hardware:
            maint_needed = st.radio("هل يحتاج نظام المراقبة صيانة خارجية فورية عبر شركة مقاولات؟", ["نعم", "لا"])
            
        submitted = st.form_submit_button("تأكيد البلاغ الاستباقي وإرساله")
        
        if submitted:
            new_ticket = {
                "القسم": alert["department"],
                "المعرف": alert["device_name"],
                "المشكلة": alert["detected_issue"],
                "صيانة مقاول": maint_needed,
                "شركة الصيانة": "قيد المعالجة",
                "تفاصيل الصيانة": "قيد المعالجة",
                "الحالة": "مفتوحة وعاجلة"
            }
            st.session_state.tickets.append(new_ticket)
            st.success("تم إرسال البلاغ لنظام المراقبة والدعم الفني بنجاح.")
            st.session_state.current_alert = get_proactive_alert()

# 2. الإدارة العليا
with tab2:
    mgmt_pass = st.text_input("أدخل كود الإدارة العليا:", type="password", key="mgmt_login")
    if mgmt_pass == "mgmt999":
        st.subheader("مؤشرات الأداء الاستراتيجية لنظام المراقبة")
        c1, c2, c3 = st.columns(3)
        c1.metric("الأعطال التي تم تلافيها استباقياً", len(st.session_state.tickets) + 12, "+4")
        c2.metric("مستوى الاستقرار العام للشبكة", "97.4%", "+1.2%")
        c3.metric("مؤشر جودة خدمات الصحة الإلكترونية", "99.1%", "+0.8%")
    elif mgmt_pass:
        st.warning("كود الإدارة غير صحيح.")

# 3. الأقسام (IT & Quality)
with tab3:
    it_pass = st.text_input("أدخل كود الدعم الفني وإدارة الأقسام:", type="password", key="it_login")
    if it_pass == "it123":
        st.subheader("إدارة ومتابعة البلاغات الاستباقية للأنظمة والجودة")
        if st.session_state.tickets:
            df = pd.DataFrame(st.session_state.tickets)
            st.table(df)
            
            st.markdown("---")
            st.subheader("إغلاق وتحديث البلاغ وتوثيق شركة المقاولات والجودة")
            with st.form("close_ticket_form"):
                ticket_index = st.selectbox("اختر البلاغ المراد تحديثه وإغلاقه:", options=range(len(st.session_state.tickets)))
                contractor_name = st.text_input("اسم شركة مقاولات الصيانة (كتابة):")
                maintenance_details = st.text_input("تفاصيل تقرير الصيانة أو الجودة (كتابة):")
                
                if st.form_submit_button("إغلاق البلاغ وتوثيقه في نظام المراقبة"):
                    st.session_state.tickets[ticket_index]["شركة الصيانة"] = contractor_name if contractor_name else "لا توجد"
                    st.session_state.tickets[ticket_index]["تفاصيل الصيانة"] = maintenance_details if maintenance_details else "لا توجد"
                    st.session_state.tickets[ticket_index]["الحالة"] = "مغلقة ومعتمدة"
                    st.success("تم تحديث البلاغ وإغلاقه بنجاح.")
                    st.rerun()
            
            if st.button("مسح السجلات المعالجة"):
                st.session_state.tickets = []
                st.rerun()
            
            csv_data = generate_stats_csv()
            if csv_data:
                st.download_button("استخراج تقرير نظام المراقبة CSV", data=csv_data, file_name="Monitoring_Report.csv", mime="text/csv")
        else:
            st.info("لا توجد بلاغات استباقية نشطة في نظام المراقبة حالياً.")
    elif it_pass:
        st.warning("كود الدخول غير صحيح.")
