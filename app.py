import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

st.set_page_config(page_title="SATR Enterprise Financial System", layout="wide")

# ---------------------------------------------------------
# 0. Gmail Notification System
# ---------------------------------------------------------
TARGET_EMAIL = "satragncy.1@gmail.com"
SENDER_EMAIL = "satragncy.1@gmail.com"
APP_PASSWORD = ""  # ضع هنا كلمة سر التطبيقات من Gmail لتفعيل الإشعارات

def send_email_async(subject, body):
    if not APP_PASSWORD:
        return
    def send_task():
        try:
            msg = MIMEMultipart()
            msg['From'] = f"SATR Security <{SENDER_EMAIL}>"
            msg['To'] = TARGET_EMAIL
            msg['Subject'] = subject
            
            html_body = f"""
            <div style="direction: rtl; text-align: right; font-family: Arial; padding: 20px; border: 1px solid #0A2842; background-color: #F8F1E9;">
                <h2 style="color: #0A2842;">SATR MARKETING AGENCY</h2>
                <div style="background-color: #FFF; padding: 15px; border-radius: 5px;">{body}</div>
                <p style="font-size: 11px; color: #827059; margin-top: 10px;">التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            """
            msg.attach(MIMEText(html_body, 'html'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"SMTP Warning: {e}")

    threading.Thread(target=send_task).start()

# ---------------------------------------------------------
# 1. Google Sheets Integration
# ---------------------------------------------------------
@st.cache_resource
def get_gspread_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    secrets_data = st.secrets["gcp_service_account"]
    info = json.loads(secrets_data["json_data"]) if "json_data" in secrets_data else dict(secrets_data)
    credentials = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(credentials)

# ---------------------------------------------------------
# 2. State & Database Initialization
# ---------------------------------------------------------
USERS = {
    "Allam@satr": {"name": "علام Admin", "pass": "mohandm2005", "role": "admin"},
    "Assem@satr": {"name": "عاصم", "pass": "444satr", "role": "user"},
    "Eissa@satr": {"name": "عيسى", "pass": "666satr", "role": "user"},
    "Mohandadel@satr": {"name": "مهند عادل", "pass": "888satr", "role": "user"},
    "mohanad": {"name": "مهند", "pass": "satr123", "role": "admin"}
}

if "emp_lists" not in st.session_state:
    st.session_state["emp_lists"] = {
        "الجرافيك ديزاين": ["لا يوجد", "أحمد", "محمد", "سارة"],
        "المونتاج والتحرير": ["لا يوجد", "عمر", "خالد"],
        "كتابة المحتوى": ["لا يوجد", "مريم", "إسلام"],
        "الميديا باير": ["لا يوجد", "علي", "يوسف"],
        "المبيعات": ["لا يوجد", "محمود (Sales)", "زياد (Sales)"]
    }

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ---------------------------------------------------------
# 3. Authentication UI
# ---------------------------------------------------------
if not st.session_state["logged_in"]:
    st.title("🔒 SATR Agency - Login")
    u = st.text_input("اسم المستخدم (Username)")
    p = st.text_input("كلمة السر (Password)", type="password")
    
    if st.button("تسجيل الدخول", type="primary"):
        if u in USERS and USERS[u]["pass"] == p:
            st.session_state["logged_in"] = True
            st.session_state["user_info"] = USERS[u]
            send_email_async(
                f"تسجيل دخول: {USERS[u]['name']}", 
                f"قام المستخدم <b>{USERS[u]['name']}</b> بتسجيل الدخول للنظام المالي."
            )
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة السر غير صحيحة")
else:
    # Sidebar: المستخدمين وتعديل قائمة الموظفين
    st.sidebar.write(f"👤 مرحباً بك: **{st.session_state['user_info']['name']}**")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("➕ إضافة موظف جديد")
    selected_dept_for_add = st.sidebar.selectbox("اختر القسم", list(st.session_state["emp_lists"].keys()))
    new_emp_name = st.sidebar.text_input("اسم الموظف الجديد")
    if st.sidebar.button("إضافة الموظف"):
        if new_emp_name.strip() and new_emp_name not in st.session_state["emp_lists"][selected_dept_for_add]:
            st.session_state["emp_lists"][selected_dept_for_add].append(new_emp_name.strip())
            st.sidebar.success(f"تمت إضافة {new_emp_name} لـ {selected_dept_for_add}")
            st.rerun()

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["logged_in"] = False
        st.rerun()

    # ---------------------------------------------------------
    # 4. Main Application UI
    # ---------------------------------------------------------
    st.title("💼 SATR Agency - Enterprise Financial System")

    tab1, tab2 = st.tabs(["📋 تسوية مشروع جديدة", "📊 عرض قاعدة البيانات أونلاين"])

    with tab1:
        st.subheader("إدخال بيانات تسوية مشروع جديدة")
        
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("اسم العميل / المشروع", "مشروع جديد")
            total_budget = st.number_input("الميزانية الكلية (EGP)", value=10000.0, step=500.0)
        with col2:
            sales_emp = st.selectbox("مسؤول المبيعات", st.session_state["emp_lists"]["المبيعات"])
            sales_comm_pct = st.number_input("نسبة عمولة المبيعات %", value=10.0)

        st.markdown("---")
        st.write("### تكاليف الفريق والميديا باير")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            gd_emp = st.selectbox("مصمم الجرافيك", st.session_state["emp_lists"]["الجرافيك ديزاين"])
            gd_qty = st.number_input("عدد التصاميم", value=5)
            gd_price = st.number_input("سعر التصميم", value=200.0)
        with c2:
            ed_emp = st.selectbox("المونتير", st.session_state["emp_lists"]["المونتاج والتحرير"])
            ed_qty = st.number_input("عدد الفيديوهات", value=2)
            ed_price = st.number_input("سعر الفيديو", value=500.0)
        with c3:
            cw_emp = st.selectbox("كاتب المحتوى", st.session_state["emp_lists"]["كتابة المحتوى"])
            cw_qty = st.number_input("عدد المنشورات", value=10)
            cw_price = st.number_input("سعر المنشور", value=100.0)

        st.markdown("---")
        mb_col1, mb_col2 = st.columns(2)
        with mb_col1:
            mb_emp = st.selectbox("الميديا باير", st.session_state["emp_lists"]["الميديا باير"])
            mb_calc_type = st.radio("طريقة حساب الميديا باير", ["مبلغ ثابت (EGP)", "نسبة مئوية (%)"])
        with mb_col2:
            if mb_calc_type == "مبلغ ثابت (EGP)":
                mb_val = st.number_input("تكلفة الميديا باير الثابتة", value=1000.0)
            else:
                mb_pct = st.number_input("نسبة الميديا باير %", value=10.0)
                mb_val = total_budget * (mb_pct / 100.0)

        # الحسابات الماليّة
        cost_gd = gd_qty * gd_price if gd_emp != "لا يوجد" else 0.0
        cost_ed = ed_qty * ed_price if ed_emp != "لا يوجد" else 0.0
        cost_cw = cw_qty * cw_price if cw_emp != "لا يوجد" else 0.0
        cost_mb = mb_val if mb_emp != "لا يوجد" else 0.0

        base_expenses = cost_gd + cost_ed + cost_cw + cost_mb
        gross_profit = total_budget - base_expenses
        sales_comm = gross_profit * (sales_comm_pct / 100.0) if sales_emp != "لا يوجد" and gross_profit > 0 else 0.0

        total_expenses = base_expenses + sales_comm
        net_profit = total_budget - total_expenses
        margin = (net_profit / total_budget * 100) if total_budget > 0 else 0.0

        st.markdown("---")
        st.write("### 📊 ملخص الفاتورة")
        m1, m2, m3 = st.columns(3)
        m1.metric("الميزانية الكلية", f"{total_budget:,.2f} EGP")
        m2.metric("إجمالي المصروفات", f"{total_expenses:,.2f} EGP")
        m3.metric("صافي الربح", f"{net_profit:,.2f} EGP", f"{margin:.1f}% هامش ربح")

        if st.button("حفظ وحفظ الشيت أونلاين 🚀", type="primary"):
            try:
                gc = get_gspread_client()
                sh = gc.open("SATR_Financial_Database")
                ws = sh.worksheet("Internal Settlements")
                
                inv_id = f"SATR-{datetime.now().strftime('%m%d%H%M')}"
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                ws.append_row([
                    inv_id, created_at, client_name, total_budget, 
                    total_expenses, net_profit, st.session_state['user_info']['name']
                ])
                
                send_email_async(
                    f"إصدار فاتورة مشروع: {client_name}",
                    f"تم إصدار الفاتورة رقم <b>{inv_id}</b> بميزانية {total_budget:,.2f} EGP وصافي ربح {net_profit:,.2f} EGP."
                )
                
                st.success("✅ تم حفظ الفاتورة بنجاح وتزامنها مع Google Sheets!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ في الشيت: {e}")

    with tab2:
        st.subheader("عرض الشيت أونلاين")
        try:
            gc = get_gspread_client()
            sh = gc.open("SATR_Financial_Database")
            worksheets = [w.title for w in sh.worksheets()]
            selected_ws = st.selectbox("اختر التبويب", worksheets)
            
            data = sh.worksheet(selected_ws).get_all_records()
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            else:
                st.info("التبويب فارغ حالياً.")
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {e}")
