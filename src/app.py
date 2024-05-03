"""
Old Bailey Case Search Application

This Streamlit-based web application enables users to search and interact with historical records from the Old Bailey API, 
which contains detailed information about court cases in England between 1674 and 1913. The app allows users to search 
for cases based on keywords, view a histogram of results by year, filter cases by date range, fetch detailed information 
about specific cases, and download this information in an Excel format.

Functions:
    to_excel(df): Converts a DataFrame into an Excel file stored in a BytesIO stream, ready for download.
    extract_date(title): Extracts and converts dates from case titles using regex, returning datetime objects.
    extract_year(title): Extracts the year from case titles using regex for histogram plotting.
    plot_histogram(df): Plots and returns a histogram of the number of cases per year using matplotlib.
    fetch_detailed_data(idkey): Fetches full text and other details for a single record from the API using the provided ID key.
    fetch_data(search_term, max_results=None): Retrieves case records from the API based on a search term and optional maximum results limit.
    fetch_all_details(filtered_df): Fetches detailed data for all records in a filtered DataFrame and returns a new DataFrame with these details.
    main(): Contains the Streamlit UI components and logic driving the application.

Usage:
    Run the application with Streamlit using the command `streamlit run app.py`. 
    Interact with the web interface to perform searches, view results, and download data.

Example:
    After starting the application, enter a search keyword such as 'theft' in the text input box. 
    Press the search button to retrieve initial results, which can then be filtered by year using the provided slider.
    Detailed case information can be fetched and downloaded post-filtering.

Notes:
    The application requires an active internet connection to fetch data from the Old Bailey API.
    Ensure all dependencies, including Streamlit, pandas, requests, matplotlib, and xlsxwriter, are installed and up-to-date.
    Adjust the `base_url` and API endpoints if the Old Bailey API specification changes.

Author:
    Jonathan Jayes
"""


import streamlit as st
import requests
import pandas as pd
from math import ceil
import datetime
import re
from io import BytesIO
import matplotlib.pyplot as plt


# Function to convert DataFrame to Excel for download
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data


# Function to extract and convert dates from the title
def extract_date(title):
    date_pattern = r'\d{1,2}(?:st|nd|rd|th)?\s\w+\s\d{4}'
    match = re.search(date_pattern, title)
    if match:
        date_str = match.group(0)
        # Remove 'th', 'st', 'nd', 'rd' from day part of the date string
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        return datetime.datetime.strptime(date_str, "%d %B %Y")
    return None

def extract_year(title):
    # Attempt to extract the year from the title string
    match = re.search(r'\d{4}', title)
    if match:
        return int(match.group(0))
    return None

def plot_histogram(df):
    # Plotting the histogram of records per year
    plt.figure(figsize=(10, 4))
    plt.hist(df['year'], bins=range(min(df['year']), max(df['year']) + 1), alpha=0.75, color='blue', edgecolor='black')
    plt.title('Number of Records per Year')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.grid(True)
    plt.tight_layout()
    return plt

# Function to fetch the full text for a single record
def fetch_detailed_data(idkey):
    url = f"https://www.dhi.ac.uk/api/data/oldbailey_record_single?idkey={idkey}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        full_text = data['hits']['hits'][0]['_source']['text']
        return full_text
    else:
        return "Failed to retrieve full text"

# Function to fetch and process data
def fetch_data(search_term, max_results=None):
    base_url = "https://www.dhi.ac.uk/api/data/oldbailey_record"
    from_param = 0
    size_param = 10  # Fetch 10 records at a time
    url = f"{base_url}?text={search_term}&from={from_param}&size={size_param}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        total_hits = data['hits']['total']
        if total_hits == 0:
            st.info("No records found for the given search term.")
            return pd.DataFrame()
        
        if max_results:
            pages = ceil(min(max_results, total_hits) / size_param)
        else:
            pages = ceil(total_hits / size_param)
        
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
                date = extract_date(record['_source']['title'])
                if date is not None:
                    row = {
                        'id': record['_id'],
                        'index': record['_index'],
                        'type': record['_type'],
                        'idkey': record['_source']['idkey'],
                        'text': record['_source']['text'],
                        'title': record['_source']['title'],
                        'images': record['_source']['images'],
                        'date': date.strftime("%Y-%m-%d"),
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


def fetch_detailed_data(idkey):
    try:
        response = requests.get(f"https://www.dhi.ac.uk/api/data/oldbailey_record_single?idkey={idkey}")
        if response.status_code == 200:
            record = response.json()['hits']['hits'][0]  # Adjusted to access the first hit directly
            source = record['_source']
            return {
                'id': record['_id'],
                'index': record['_index'],
                'type': record['_type'],
                'idkey': source['idkey'],
                'title': source['title'],
                'images': source['images'],
                'text': source['text']
            }
        else:
            st.error(f"Failed to fetch details for ID {idkey}: HTTP {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred while fetching details for ID {idkey}: {str(e)}")
        return None

def fetch_all_details(filtered_df):
    details = []
    progress_bar = st.progress(0)
    for i, record in enumerate(filtered_df.itertuples()):
        detail = fetch_detailed_data(record.idkey)
        if detail:
            details.append(detail)
        progress_bar.progress((i + 1) / len(filtered_df))
    progress_bar.empty()
    return pd.DataFrame(details)


def main():
    st.title("Old Bailey Case Search")

    # Search term input
    search_term = st.text_input("Enter search keyword:", "")
    if search_term:
        if 'search_results' not in st.session_state or st.session_state.search_term != search_term:
            st.session_state.search_results = fetch_data(search_term)
            st.session_state.search_term = search_term

        if not st.session_state.search_results.empty:
            search_results = st.session_state.search_results
            search_results['year'] = search_results['title'].apply(extract_year)
            # st.dataframe(search_results[['id', 'title', 'year']])
            hist_plot = plot_histogram(search_results)
            st.pyplot(hist_plot)

            year_min = st.session_state.search_results['date'].min()[:4]
            year_max = st.session_state.search_results['date'].max()[:4]
            years = st.slider("Select Year Range", int(year_min), int(year_max), (int(year_min), int(year_max)))

            filtered_df = st.session_state.search_results[st.session_state.search_results['date'].between(f"{years[0]}-01-01", f"{years[1]}-12-31")]

            if st.button("Fetch Details for All in Range"):
                df_detailed = fetch_all_details(filtered_df)
                if not df_detailed.empty:
                    st.write(df_detailed)
                    excel_data = to_excel(df_detailed)
                    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                    safe_search_term = "".join([c for c in search_term if c.isalnum() or c in [' ', '-', '_']]).rstrip()
                    file_name = f'old-bailey-{safe_search_term}-{current_datetime}-{year_min}-{year_max}.xlsx'
                    st.download_button(
                        label="Download Excel file",
                        data=excel_data,
                        file_name=file_name,
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )

if __name__ == "__main__":
    main()
