import streamlit as st
import pandas as pd
from datetime import date
from demoData_generator import generate_large_dataset_in_chunks  # Your function here

# --- Page Config ---
st.set_page_config(page_title="Phocas AI Demo Generator", layout="wide")

# --- Apple-Inspired Custom CSS ---
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #1c1c1e;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        .stTextInput>div>div>input, .stTextArea>div>textarea, .stDateInput>div>input {
            border-radius: 12px;
            padding: 0.6rem;
            border: 1px solid #ccc;
        }
        .stButton>button {
            background-color: #007aff;
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #005ee6;
            transform: translateY(-1px);
        }
        .stDownloadButton>button {
            border-radius: 12px;
            background-color: #f2f2f7;
            color: #007aff;
            border: 1px solid #ccc;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("📊 Phocas AI Demo Data Generator")

# --- Sidebar ---
with st.sidebar:
    st.header("🔧 Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", help="Used one-time only. Not stored.")

    start_date = st.date_input("Start Date", value=date(2024, 1, 1))
    end_date = st.date_input("End Date", value=date(2024, 3, 31))

    total_rows = st.number_input("Total Rows", min_value=100, max_value=5000, step=100, value=1000)
    chunk_size = st.number_input("Chunk Size", min_value=100, max_value=1000, step=100, value=250)

    dimensions_input = st.text_area("Dimensions", value="Customer, Region, Product")
    measures_input = st.text_area("Measures", value="Quantity, Value, Profit $")

    trend_config = st.text_area(
        "Optional Trend Rules",
        placeholder="E.g., Sales spike at end of month",
        help="Describe business trends you'd like reflected in the data"
    )

# --- Validate Inputs ---
if start_date > end_date:
    st.error("⚠️ Start Date cannot be after End Date.")
    st.stop()

run_button = st.button("🚀 Generate Dataset")

# --- Main Logic ---
if run_button and api_key:
    with st.spinner("Generating data... this may take up to a minute ⏳"):
        dimensions = [d.strip() for d in dimensions_input.split(",") if d.strip()]
        measures = [m.strip() for m in measures_input.split(",") if m.strip()]

        try:
            df = generate_large_dataset_in_chunks(
                key=api_key,
                dimensions=dimensions,
                measures=measures,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                total_rows=total_rows,
                chunk_size=chunk_size,
                trend_config=trend_config
            )
        except Exception as e:
            st.error(f"❌ Error: {e}")
            df = None

        if df is not None:
            st.success("✅ Dataset generated!")

            preview_rows = st.slider("Preview rows", min_value=5, max_value=50, value=10)
            st.dataframe(df.head(preview_rows), use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="sales_demo_data.csv", mime="text/csv")
        else:
            st.error("⚠️ Failed to generate dataset. Check API key or trend formatting.")
elif run_button and not api_key:
    st.warning("🔑 Please enter your OpenAI API key.")
