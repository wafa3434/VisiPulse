import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="VisiPulse - Health Cluster Proactive System", layout="wide")

# --- الترويسة العليا (شعار + ترجمة) ---
header_col1, header_col2, header_col3 = st.columns([2, 5, 1])

# اختيار اللغة
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
    st.subheader("شاشة التنبيهات الاستباقية" if lang == "العربية (AR)" else "Proactive Alerts Screen")
    st.warning("تنبيه استباقي (VisiPulse): تم رصد مؤشرات تراجع في أداء الجهاز (DEV-101)." if lang == "العربية (AR)" else "Proactive Alert: Performance degradation detected in (DEV-101).")
    if st.button("تأكيد استلام التنبيه" if lang == "العربية (AR)" else "Confirm Receipt"):
        st.success("تم التأكيد بنجاح" if lang == "العربية (AR)" else "Confirmed successfully")

with tab2:
    portal_label = "اختر البوابة:" if lang == "العربية (AR)" else "Choose Portal:"
    portals = ["قسم تقنية المعلومات (IT)", "الإدارة العليا (Upper Management)"] if lang == "العربية (AR)" else ["IT Department", "Upper Management"]
    portal_choice = st.radio(portal_label, portals)
    
    # بوابة الإدارة العليا
    if "الإدارة العليا" in portal_choice or "Upper Management" in portal_choice:
        mgmt_passcode = st.text_input("أدخل كود الإدارة:" if lang == "العربية (AR)" else "Enter Password:", type="password")
        if mgmt_passcode == "mgmt999":
            st.markdown("### 🎯 " + ("لوحة المؤشرات الاستراتيجية" if lang == "العربية (AR)" else "Strategic Indicators Dashboard"))
            
            # بيانات الإدارة العليا
            chart_data = pd.DataFrame({"الكفاءة %": [88, 90, 92, 91, 93, 94.8]}, index=["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"] if lang == "العربية (AR)" else ["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
            st.area_chart(chart_data)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("الأعطال المتفاداة" if lang == "العربية (AR)" else "Failures Prevented", "28", "+5")
            c2.metric("نسبة الاستقرار" if lang == "العربية (AR)" else "Stability Rate", "94.8%", "+3.2%")
            c3.metric("التوفير المالي" if lang == "العربية (AR)" else "Financial Savings", "150K", "+12%")

    # بوابة تقنية المعلومات (IT)
    elif "قسم تقنية المعلومات" in portal_choice or "IT Department" in portal_choice:
        it_passcode = st.text_input("أدخل كود الـ IT:" if lang == "العربية (AR)" else "Enter IT Password:", type="password")
        if it_passcode == "it123":
            sub_tabs = ["مدير الصحة الإلكترونية (e-Health)", "قسم الجودة (Quality)"] if lang == "العربية (AR)" else ["e-Health Manager", "Quality Department"]
            sub_tab = st.selectbox("اختر القسم:", sub_tabs)
            
            if "e-Health" in sub_tab:
                st.markdown("### 📊 " + ("لوحة مراقبة الصحة الإلكترونية" if lang == "العربية (AR)" else "e-Health Dashboard"))
                st.bar_chart(pd.DataFrame({'الجاهزية %': [99.2, 98.5, 99.8, 99.5]}, index=["سيرفر 1", "سيرفر 2", "سيرفر 3", "سيرفر 4"]))
            
            elif "الجودة" in sub_tab or "Quality" in sub_tab:
                st.markdown("### 📈 " + ("لوحة جودة البيانات" if lang == "العربية (AR)" else "Data Quality Dashboard"))
                st.line_chart(pd.DataFrame({"فعلي": [2.1, 1.8, 3.2, 2.5], "مستهدف": [2.0, 2.0, 2.0, 2.0]}, index=["وحدة 1", "وحدة 2", "وحدة 3", "وحدة 4"]))
