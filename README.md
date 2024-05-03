# Old Bailey Records Wrapper

This repository contains the source code for a Streamlit web application that enables users to search and interact with historical records from the Old Bailey Online API. The API covers court cases in England between 1674-1913, providing a rich dataset of legal history.

## Features

- **Search Functionality:** Users can search for cases based on keywords.
- **Histogram of Results:** View distribution of cases over years.
- **Filter by Date:** Users can narrow down search results within a specific date range.
- **Detailed Case Information:** Fetch and display detailed information for individual cases.
- **Download Data:** Download detailed case information in Excel format.

## Getting Started

### Prerequisites

Before running the application, ensure you have the following installed:
- Python 3
- Streamlit
- Pandas
- Requests
- Matplotlib
- XlsxWriter

You can install the necessary libraries using pip:

```bash
pip install streamlit pandas requests matplotlib xlsxwriter
```

### Running the Application

To run the app, navigate to the directory containing `app.py` and run the following command:

```bash
streamlit run app.py
```

## Usage

1. **Start the Application:** Open your terminal and use the command above to start the app.
2. **Enter a Search Keyword:** Use the text input box to enter terms such as 'theft', 'murder', etc.
3. **View Results:** Initial search results can be filtered by year using a slider.
4. **Fetch and Download:** After filtering, you can fetch detailed case information and download it as an Excel file.

## Example

After starting the application:
- Input 'theft' in the search box.
- Hit the search button to load results.
- Use the slider to filter results by year.
- Press 'Fetch Details for All in Range' to get detailed data.
- Use the 'Download Excel file' button to download the data.

## Author

- Jonathan Jayes