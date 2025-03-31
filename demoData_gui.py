import streamlit as st
import pandas as pd
from datetime import date, datetime
from demoData_generator import generate_large_dataset_in_chunks  # Replace with your function path

st.set_page_config(page_title="Phocas AI Demo Data Generator", layout="wide")

st.title("📊 Phocas AI Demo Data Generator")
st.text("Built by Hayden Poore")
# --- Sidebar Inputs ---
# --- Sidebar Inputs ---
with st.sidebar:
    st.header("🔧 Configuration")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    start_date = st.date_input("Start Date", value=date(2024, 1, 1))
    end_date = st.date_input("End Date", value=(datetime.today()))
    total_rows = st.number_input("Total Rows (Transactions)", min_value=1, max_value=50000, step=100, value=100)
    #chunk_size = st.number_input("Chunk Size", min_value=100, max_value=1000, step=100, value=250)
    dimensions_input = st.text_area("Dimensions (comma-separated)", value="Customer, Region, Product")
    measures_input = st.text_area("Measures (comma-separated)", value="Quantity, Value, Cost, Profit $")
    trend_config = st.text_area("Optional Trend Rules and Prompt Additions", placeholder="E.g., Sales spike at end of month")

# --- Run Button in Main Area ---
# Validate date inputs
if start_date > end_date:
    st.error("⚠️ Start Date cannot be after End Date.")
    st.stop()

run_button = st.button("🚀 Generate Dataset")


# --- Main Logic ---
if run_button and api_key:
    with st.spinner("Generating data... this may take up to a minute ⏳"):
        dimensions = [d.strip() for d in dimensions_input.split(",") if d.strip()]
        measures = [m.strip() for m in measures_input.split(",") if m.strip()]

        df = generate_large_dataset_in_chunks(
            key=api_key,
            dimensions=dimensions,
            measures=measures,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            total_rows=total_rows,
            chunk_size=250,
            trend_config=trend_config
        )

        if df is not None:
            st.success("✅ Dataset generated!")
            st.dataframe(df.head(10))

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name=f"sales_demo_data.csv", mime="text/csv")
        else:
            st.error("⚠️ Failed to generate dataset. Check API key or prompt formatting.")

elif run_button and not api_key:
    st.warning("🔑 Please enter your OpenAI API key.")
