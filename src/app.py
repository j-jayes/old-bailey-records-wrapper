import streamlit as st
import requests
import pandas as pd
from math import ceil
from io import BytesIO
import re

# Function to extract dates from the title
def extract_date(title):
    date_pattern = r'\d{1,2}(?:st|nd|rd|th)?\s\w+\s\d{4}'  # Matches dates in the format "12th January 1800"
    match = re.search(date_pattern, title)
    if match:
        return match.group(0)
    return "Unknown"

# Function to convert DataFrame to Excel for download
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# Function to fetch and process data
def fetch_data(search_term):
    base_url = "https://www.dhi.ac.uk/api/data/oldbailey_record"
    from_param = 0
    size_param = 10
    url = f"{base_url}?text={search_term}&from={from_param}&size={size_param}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        total_hits = data['hits']['total']
        pages = ceil(total_hits / size_param)
        # set pages to 2 for testing
        pages = 2
        rows = []
        
        progress_bar = st.progress(0)
        status_message = st.empty()
        
        for page in range(pages):
            status_message.text(f"Fetching page {page + 1} of {pages}...")
            if page != 0:
                from_param = page * size_param
                url = f"{base_url}?text={search_term}&from={from_param}&size={size_param}"
                response = requests.get(url)
                if response.status_code != 200:
                    st.error("Failed to fetch data on subsequent pages.")
                    return pd.DataFrame()
                data = response.json()
            
            records = data['hits']['hits']
            for record in records:
                row = {
                    'id': record['_id'],
                    'index': record['_index'],
                    'type': record['_type'],
                    'idkey': record['_source']['idkey'],
                    'text': record['_source']['text'],
                    'title': record['_source']['title'],
                    'images': record['_source']['images'],
                    'date': extract_date(record['_source']['title'])
                }
                rows.append(row)
            
            progress_bar.progress((page + 1) / pages)

        status_message.text("Fetching complete.")
        progress_bar.empty()
        
        df = pd.DataFrame(rows)
        return df
    else:
        st.error("Failed to retrieve data: " + str(response.status_code))
        return pd.DataFrame()

# Streamlit user interface setup
st.title("Old Bailey Records Search")
search_term = st.text_input("Enter a search term:", "theft")
if st.button("Fetch Data"):
    with st.spinner('Fetching data...'):
        df = fetch_data(search_term)
        if not df.empty:
            st.write(df)
            excel_data = to_excel(df)
            st.download_button(
                label="Download Excel file",
                data=excel_data,
                file_name=f'old-bailey-{search_term}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            st.success('Data fetched successfully!')
