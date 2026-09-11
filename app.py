import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

st.set_page_config(page_title="SATR Agency Financial System", layout="wide")
st.title("💼 SATR Agency Financial Management System")

@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    secrets_data = st.secrets["gcp_service_account"]
    if "json_data" in secrets_data:
        info = json.loads(secrets_data["json_data"])
    else:
        info = dict(secrets_data)
        
    credentials = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(credentials)

try:
    gc = get_gspread_client()
    st.success("✅ Connected successfully to Google Sheets!")
    
    sheet_name = st.text_input("Enter your Google Sheet Name:", "SATR_Financial_Database")
    
    if sheet_name:
        sh = gc.open(sheet_name)
        
        # جلب جميع التبويبات المتاحة داخل الشيت
        worksheets = [ws.title for ws in sh.worksheets()]
        selected_ws = st.selectbox("Select Sheet Tab / التبويب:", worksheets)
        
        worksheet = sh.worksheet(selected_ws)
        data = worksheet.get_all_records()
        
        if data:
            df = pd.DataFrame(data)
            st.subheader(f"📊 Overview: {selected_ws}")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"التبويب '{selected_ws}' فارغ حالياً، يرجى إضافة بيانات أو اختيار تبويب آخر.")

except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")
