import zipfile
import pandas as pd
import os
import io
import base64
import streamlit as st
from datetime import datetime
# At the top of app.py
st.set_page_config(
    page_title="ZIP CSV Processor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
def process_zip_file(uploaded_zip_file):
    """
    Extracts a CSV file from an uploaded ZIP archive, renames specific column headers,
    and returns the processed dataframe and CSV.
    
    Args:
        uploaded_zip_file: The uploaded ZIP file from Streamlit
    
    Returns:
        tuple: (processed_df, csv_string, csv_filename)
    """
    # Create a BytesIO object from the uploaded file
    zip_bytes = io.BytesIO(uploaded_zip_file.read())
    
    # Extract the zip file
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        # List all files in the ZIP
        file_list = zip_ref.namelist()
        
        # Find CSV files
        csv_files = [f for f in file_list if f.lower().endswith('.csv')]
        
        if not csv_files:
            st.error("No CSV files found in the ZIP archive")
            return None, None, None
        
        # Extract the first CSV file found
        csv_file = csv_files[0]
        st.info(f"Found CSV file: {csv_file}")
        
        # Extract the CSV content
        csv_content = zip_ref.read(csv_file)
        
        # Convert to a pandas dataframe
        df = pd.read_csv(io.BytesIO(csv_content))
    
    # Define the mapping of old column names to new ones
    column_mapping = {
        'Campaign Id': 'Campaign__Campaign_Id',
        'Campaign Name': 'campaign__name',
        'Entered': 'campaign__campaign_start_date',
        'Sent Date': 'Date__date',
        'Published': 'Contacted_Customers',
        'Sent': 'Msg_Sent',
        'Delivered': 'Msg_Delivered',
        'Unique Opened': 'Unique_Open_Count',
        'Unique Opened %': 'Unique_Click_Count'
    }
    
    # Display original columns for verification
    st.write("Original columns:", df.columns.tolist())
    
    # Rename columns based on the mapping
    # Only rename columns that exist in the dataframe
    rename_dict = {old: new for old, new in column_mapping.items() if old in df.columns}
    df = df.rename(columns=rename_dict)
    
    # Display the new column names
    st.write("Renamed columns:", df.columns.tolist())
    
    # Generate output file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"processed_{timestamp}.csv"
    
    # Convert dataframe to CSV string
    csv_string = df.to_csv(index=False)
    
    return df, csv_string, output_filename

def get_download_link(csv_string, filename):
    """Generates a link to download the CSV file"""
    b64 = base64.b64encode(csv_string.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Processed CSV</a>'
    return href

def main():
    st.title("ZIP CSV Processor")
    st.write("Upload a ZIP file containing a CSV to process and rename the headers.")
    
    uploaded_file = st.file_uploader("Choose a ZIP file", type="zip")
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        # Add a process button
        if st.button("Process ZIP File"):
            with st.spinner("Processing..."):
                # Process the ZIP file
                processed_df, csv_string, filename = process_zip_file(uploaded_file)
                
                if processed_df is not None:
                    # Display a sample of the processed data
                    st.subheader("Preview of Processed Data")
                    st.dataframe(processed_df.head())
                    
                    # Provide download link
                    st.subheader("Download Result")
                    st.markdown(get_download_link(csv_string, filename), unsafe_allow_html=True)
                    
                    # Show data statistics
                    st.subheader("Data Statistics")
                    st.write(f"Total rows: {len(processed_df)}")
                    st.write(f"Total columns: {len(processed_df.columns)}")
                    
                    # Additional metrics in columns
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Rows Processed", f"{len(processed_df):,}")
                    with col2:
                        st.metric("Columns Renamed", f"{len(rename_dict)}")

if __name__ == "__main__":
    main()
