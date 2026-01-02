import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(page_title="SD College Graduation Data", layout="wide")

# The dynamic link to your Google Sheet (CSV export format)
SHEET_ID = "1LNHrVooUxwzmO9lQ3w8tlbZTtHQbCbMXemk8qGcycLQ"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)  # Refreshes every 5 minutes
def load_data():
    df = pd.read_csv(DATA_URL)
    
    # Clean Annual CTC column: Keep only numbers for calculation
    # Column name: "If placed, what is the annual CTC (salary) including all benefits?"
    salary_col = "Annual CTC (₹ per year) : Annual CTC refers to the total yearly compensation offered by the employer (Annual Gross Salary including Basic + allowances + bonuses+PF ) (not monthly take home salary). Please enter digits only, without commas, and do not add “Rs.” or the rupee symbol or any words.
Example: 430000"
    df[salary_col] = pd.to_numeric(df[salary_col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce')
    
    # Ensure Year is numeric
    # Column name: "Year of graduation (completion of program)"
    year_col = "Year of graduation (completion of program)"
    df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
    
    return df

try:
    df = load_data()
    
    # Exact Column Names from your Sheet
    col_dept = "Department"
    col_program = "Name of the Program completed"
    col_stipulated = "Whether completed the program in stipulated time (eg: 3 years for UG and 2 years for PG)?"
    col_status = "Status"
    col_year = "Year of graduation (completion of program)"
    col_salary = "If placed, what is the annual CTC (salary) including all benefits?"

    st.title("🎓 Graduation Outcome Dashboard")
    st.info("Data is pulled dynamically from the Google Sheet.")

    # --- Section 1: Department Statistics ---
    st.header("Department-wise Statistics")
    
    # Grouping logic
    stats = df.groupby([col_dept, col_program]).agg(
        Total_Students=('Full Name', 'count'),
        Passed_Stipulated_Time=(col_stipulated, lambda x: (x.astype(str).str.strip().str.lower() == 'yes').sum()),
        Placed_Count=(col_status, lambda x: (x == 'Placed / Employed').sum()),
        Higher_Studies_Count=(col_status, lambda x: (x == 'Higher Studies').sum())
    ).reset_index()

    st.dataframe(stats, use_container_width=True)

    # --- Section 2: Salary Analysis (2023, 2024, 2025) ---
    st.header("Salary Analysis (2023 - 2025)")
    
    # Filtering for the specific years and only placed students
    target_years = [2023, 2024, 2025]
    salary_df = df[
        (df[col_year].isin(target_years)) & 
        (df[col_status] == 'Placed / Employed') & 
        (df[col_salary].notnull())
    ]

    if not salary_df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Minimum Salary", f"₹{salary_df[col_salary].min():,.2f}")
        m2.metric("Maximum Salary", f"₹{salary_df[col_salary].max():,.2f}")
        m3.metric("Median Salary", f"₹{salary_df[col_salary].median():,.2f}")
        
        # Breakdown by year for clarity
        st.subheader("Summary Table by Graduation Year")
        year_summary = salary_df.groupby(col_year)[col_salary].agg(['min', 'max', 'median', 'count']).rename(columns={'count': 'Students Placed'})
        st.table(year_summary)
    else:
        st.warning("No placement salary data found for graduation years 2023, 2024, or 2025.")

except Exception as e:
    st.error(f"Error processing data: {e}")
    st.info("Ensure the Google Sheet is set to 'Anyone with the link can view'.")
