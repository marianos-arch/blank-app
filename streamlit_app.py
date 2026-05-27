from asyncio import run
import pandas as pd
import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Excel/CSV to Pipe TXT", layout="centered")

st.title("My quick app")
#st.write(
#    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
#)

st.title("📄 Excel/CSV → Pipe-Delimited TXT")
st.write(
    "Upload an Excel workbook and download its first worksheet as a pipeline-delimited .txt file."
)
# 1. Let the user choose between Excel and CSV
file_format = st.radio(
    "Select your input file format:",
    options=["Excel", "CSV"],
    horizontal=True,
)

def file_to_pipe_txt(uploaded_file, file_type) -> tuple[str, pd.DataFrame]:
    """Convert Excel or CSV to pipe-delimited text and return both text and the raw dataframe"""
    # 1. Read file based on user selection
    if file_type == "Excel":
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        df = pd.read_csv(uploaded_file)
    
    if df.empty:
        return "", df

    # 2. Fix Dates FIRST
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%m/%d/%Y')
        elif df[col].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}').any():
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%m/%d/%Y')

    # 3. Clean up float numbers (removes '.0')
    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].apply(lambda x: str(int(x)) if pd.notnull(x) and x.is_integer() else x)

    # 4. Replace remaining NaN/NaT values with empty strings
    cleaned = df.fillna('')
    
    # 5. Convert cells to strings, STRIPIING ALL LEADING/TRAILING SPACES
    lines = []
    for _, row in cleaned.iterrows():
        row_values = []
        for val in row:
            val_str = str(val).strip()  # Removes leading/trailing spaces dynamically
            # Safety check for persistent 'nan' text strings
            if val_str.lower() == 'nan':
                val_str = ""
            row_values.append(val_str)
            
        row_str = "|".join(row_values)
        lines.append(row_str)
        
    # 6. Use Windows Carriage Return Line Feed (\r\n) as required by specifications
    return "\r\n".join(lines), df

uploaded_file = st.file_uploader(
    f"Choose an {file_format} file ",
    type=file_type,
    help=f"Supports .{file_types[0]} files.",
)

if uploaded_file is not None:
    try:
        #get both the text layout and the df back from our function
        text, df = file_to_pipe_txt(uploaded_file, file_format)

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
        st.error("Conversion failed. Please make sure the file is a valid {file_format} file.")
        st.exception(exc)

 # st run streamlit_app.py



