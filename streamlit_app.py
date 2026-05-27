from asyncio import run
import pandas as pd
import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Excel to Pipe TXT", layout="centered")

st.title("My quick app")
#st.write(
#    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
#)

st.title("📄 Excel → Pipe-Delimited TXT")
st.write("Upload an Excel workbook and download its first worksheet as a pipeline-delimited .txt file.")


def excel_to_pipe_txt(uploaded_file) -> str:
    #Convert the first worksheet of an Excel file to pipe-delimited text.
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    if df.empty:
        return ""

    # Clean up NaN values
    cleaned = df.fillna("").astype(str)
    
    # FIX: Initialize as an empty list to remove the header row
    lines = []
    
    # FIX: Explicitly convert every cell value in the row to a string before joining
    lines.extend("|".join(str(val) for val in row) for _, row in cleaned.iterrows())

    # 2. Automatically find and reformat all date columns
    for col in df.columns:
    # Check if the column contains datetime data
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%m/%d/%Y')
    # If it's read as text but looks like a timestamp (YYYY-MM-DD)
        elif df[col].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}').any():
            df[col] = pd.to_datetime(df[col], errors='ignore').dt.strftime('%m/%d/%Y')

# 3. Clean up the rest of your data (nan handling, etc.)
    df = df.fillna('')
        
    return "\n".join(lines)


uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=["xlsx", "xls"],
    help="Supports .xlsx and .xls files.",
)

if uploaded_file is not None:
    try:
        text = excel_to_pipe_txt(uploaded_file)
        df = pd.read_excel(uploaded_file)

        st.success(f"Converted {uploaded_file.name} successfully.")
        st.download_button(
            label="Download .txt",
            data=text,
            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.txt",
            mime="text/plain",
            use_container_width=True,
        )

        with st.expander("Preview", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)

        st.caption("Output format uses '|' as the delimiter and new lines for each row. Note: header removed")
        st.code(text[:4000], language="text")
    except Exception as exc:
        st.error("Conversion failed. Please make sure the file is a valid Excel workbook.")
        st.exception(exc)

 # st run streamlit_app.py



