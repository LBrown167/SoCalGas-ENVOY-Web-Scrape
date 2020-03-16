# Header  --------
# This script requires use of ChromeDriver
# ChromeDriver is a separate executable that Selenium WebDriver uses to control Chrome
# The version of the ChromeDriver required depends on the version of Chrome installed
# If your version says version 80.0.3987.122 (Official Build) (64-bit) = version
# So download the appropriate version: https://chromedriver.chromium.org/downloads
# This script does not require credentials
# ------------------------------------------------------------------
# Modules
# ------------------------------------------------------------------

import pandas as pd
import warnings

# splinter allows for visiting URLs and interacting with items
from splinter import Browser
from bs4 import BeautifulSoup as bs
import time

# ------------------------------------------------------------------
# Function
# ------------------------------------------------------------------

def Scrape():
    """Function to scrape OFO history by:
     1) Initiating ChromeDriver
     2) Navigating to relevant SoCal Gas html sites (high and low OFO history)
     3) Pulling, reformatting, and exporting tabular data in csv file format """


    # Define the path to ChromeDriver, initiate the Browser instance
    # Print a message
    executable_path = {"executable_path": "C:/Users/LBro/Desktop/chromedriver.exe"}
    browser = Browser("chrome", **executable_path, headless=True)
    print("CHROME DRIVER NOW RUNNING...")

    # List of http addresses to visit and scrape from the interwebs
    ofo_list = ["https://scgenvoy.sempra.com/#nav=/Public/ViewExternalOFO.getOFO",
                "https://scgenvoy.sempra.com/#nav=/Public/ViewExternalLowOFO.getLowOFO"]

    # For each item in the OFO list - visit that html and use the proper 'click' to navigate to place containing data
    # Also obtaining part of the string that will be used in CSV export
    for ofo_i in ofo_list:
        print(ofo_i)
        browser.visit(ofo_i)
        time.sleep(2)
        if 'Low' in ofo_i:
            browser.click_link_by_partial_text('Low OFO/EFO Event History')
            file_name = 'lowofo'
        else:
            browser.click_link_by_partial_text('High OFO Event History')
            file_name = 'highofo'

        # Obtain all the html on the site
        # 'table' is everything, 'header_rows' are headers from 'table', and ledger_data is content from 'table'
        time.sleep(5)
        html = browser.html
        soup = bs(html, 'html.parser')
        table = soup.find('table', {'class': 'ledger_table'})
        header_rows = table.find_all("td", {"class": "header_row"})
        ledger_data = table.find_all("td", {"class": "ledger_data"})

        # Get the OFO data into lists for easy comprehension (first headers then body ('ledger') of table)
        # Initiate empty list then append html data into a list
        # Remove the '\xa0' string to obtain solely the content
        # All headers (YYYY) and data are in these lists (lists contains data from many years)
        headers_raw = []
        for each in header_rows:
            headers_raw.append(each.text)

        headers = []
        for each in headers_raw:
            header_rows_cleaned = each.strip('\xa0')
            headers.append(header_rows_cleaned)

        ledger_raw = []
        for each in ledger_data:
            ledger_raw.append(each.text)

        ledger = []
        for each in ledger_raw:
            header_rows_cleaned = each.strip('\xa0')
            ledger.append(header_rows_cleaned)

        # This is a way of getting only the most recent year's data (left-hand column) - a clever way
        # The data in ledger is pulled in one long string with the top row first, then second, etc.
        # ledger[1::len(headers)] uses the number of columns of data to pull only left-most column because:
        # The 1 means pull data starting at position 1 where data in position 1 is the first entry in the left-most column
        # (Actual first item in position 0 is blank)
        # And then pull every element after that in position spaced at same interval length as number of columns
        # So skips over all the other column values and pulls the second row item in the first column, etc
        ofo_final = []
        for each in ledger[1::len(headers)]:
            print(each)
            ofo_final.append(each)

        # Convert list to to DataFrame: clean header (just most recent year 'YYYY') and ledger content
        # Remove NA values, split headers by comma
        # Rename the columns
        df = pd.DataFrame({headers[0]: ofo_final})
        df = df.dropna(axis=0, how='any')
        df = df[str(headers[0])].str.split(',', expand=True)

        # Create date column first position column (Month and Day) and year obtained from the header
        # Rename rows where the data are blank in first position column
        df = df.rename(columns={0: 'Month_Day', 1: 'Stage', 2: 'Percent'})
        df['Date'] = df['Month_Day'] + ", " + str(headers[0])
        df = df[df['Month_Day'] != '']
        df = df.drop(columns=['Month_Day'])

        # Export the file
        return df.to_csv(file_name + str(headers[0]) + '.csv', index=False)

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

warnings.filterwarnings('ignore')
Scrape()