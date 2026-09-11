import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Satr Agency Financial System", layout="wide")

st.title("💼 SATR Agency Financial Management System")

# Connect to Google Sheets using Streamlit Secrets
@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    return gspread.authorize(credentials)

try:
    gc = get_gspread_client()
    st.success("✅ Connected successfully to Google Sheets!")
    
    # Input field for Spreadsheet Name or URL
    sheet_name = st.text_input("Enter your Google Sheet Name:", "SATR_Financial_Database")
    
    if sheet_name:
        sh = gc.open(sheet_name)
        worksheet = sh.get_worksheet(0)
        data = worksheet.get_all_records()
        
        if data:
            df = pd.DataFrame(data)
            st.subheader("📊 Financial Overview")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("The selected worksheet is empty.")

except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")
