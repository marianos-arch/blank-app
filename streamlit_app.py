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
    """Convert the first worksheet of an Excel file to pipe-delimited text."""
    # 1. Read the Excel file, keeping it raw
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    if df.empty:
        return ""

    # 2. Fix Dates FIRST (while they are still recognized as dates/numbers)
    for col in df.columns:
        # If the column is naturally recognized as datetime data
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%m/%d/%Y')
        # If it's read as text/object but matches a YYYY-MM-DD pattern
        elif df[col].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}').any():
            # errors='coerce' turns bad formats to NaT instead of crashing, then we format
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%m/%d/%Y')

    # 3. Clean up float numbers (removes '.0' from numbers like 2.0, 5.0)
    for col in df.columns:
        # Check if the column is numeric float
        if pd.api.types.is_float_dtype(df[col]):
            # Convert to nullable integer if they are whole numbers, otherwise keep as string
            # This safely removes '.0' without crashing on actual decimals or blanks
            df[col] = df[col].apply(lambda x: str(int(x)) if pd.notnull(x) and x.is_integer() else x)

    # 4. Replace remaining NaN/NaT values with empty strings
    cleaned = df.fillna('')
    
    # 5. Convert every cell to a string and join with pipes (skipping header)
    lines = []
    for _, row in cleaned.iterrows():
        # Clean up any lingering text 'nan' strings and join
        row_str = "|".join("" if str(val).lower() == 'nan' else str(val) for val in row)
        lines.append(row_str)
        
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



