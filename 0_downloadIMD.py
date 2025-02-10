"""
DOWNLOAD IMD DATA FROM IMD WEBSITE

Some prerequisites are required to run this code:
    1. Update Chrome to the latest version

    2. Download the latest chromedriver for your browser and system from the given site:
        https://googlechromelabs.github.io/chrome-for-testing/

    3. Install and upgrade selenium package through command window
        pip install selenium
        pip install --upgrade selenium
        (Replace 'pip' with 'conda' for installing into an Anaconda environment)

* The variables that need to be adjusted are given from lines 60 to 66 *
    + Path to the folder in which the IMD files need to be saved: "output_folder"
    + Path to the chromedriver installed: "chromeDriver"
    + Type of variable: "var_type" (archive, realtime)
        - archive: Gridded Data Archive
        - realtime: Gridded Data Real Time
    + Variable to download: "var" (rain, temp_max or temp_min)
        - rainNC = Rainfall (netCDF)
            archive - 0.25 x 0.25 resolution (1901 to 2023)
        - rainBIN = Rainfall (Binary)
            archive - 0.25 x 0.25 resolution (1901 to 2024)
            realtime - 0.25 x 0.25 resolution (01/01/2022 - present)
        - temp_max = Maximum temperature (Binary)
            archive - 1.0 x 1.0 resolution (1951 - 2024)
            realtime - 0.5 x 0.5 resolution (01/06/2015 - present)
        - temp_min = Minimum temperature (Binary)
            archive - 1.0 x 1.0 resolution (1951 - 2024)
            realtime - 0.5 x 0.5 resolution (01/06/2015 - present)
    + First year to download data for: "start_year"
    + Last year to download data for: "end_year"

# IF ANY FILE IS BEING SKIPPED, stop the process - go to line 186 and increase time.sleep(2) to a higher value
    - This can occur while downloading real time data
# Please note that due to automatic bot detection, the Chrome window that is launched can stop working mid-code
    - happens mostly for realtime data due to the volume of data that needs to be downloaded
    - check till which year the download has been completed for all days
    - restart from the new year (inbuilt check is coded to avoid duplicate downloads)

                                        -k.r.bro_05
"""

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.support.ui import Select
import time
import os
import sys
import re

# Variables to be edited
output_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\0_IMDraw"
chromeDriver = r"C:\Users\koust\Downloads\Python\chromedriver-win64\chromedriver.exe"
var_type = 'realtime'
var = 'temp_min'
start_year = 2023
end_year = 2024

# Checking compatibility of Chrome and chromeDriver
try:
    driver = webdriver.Chrome(service=Service(chromeDriver))
    driver.quit()
except SessionNotCreatedException:
    print("Update Chrome and download the latest ChromeDriver (line 5, 7)")
    sys.exit()

# Function to set up and launch chromeDriver
def chrome_launch(webpage):
    global driver
    # Settings for chromeDriver
    options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "profile.default_content_setting_values.notifications": 1
    }
    options.add_experimental_option("prefs", prefs)

    # Setting up the driver
    service = Service(chromeDriver)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(webpage)

# Function to check if there are any incomplete downloads
def wait_for_downloads(directory, check_interval=5):
    print("Waiting for downloads to finish...")
    while any([filename.endswith('.crdownload') for filename in os.listdir(directory)]):
        time.sleep(check_interval)
    print("All downloads completed.")

# Function to download Gridded Data Archive
def archive_download(start, end, dropdown_id, webpage):
    chrome_launch(webpage=webpage)

    # Locate the year dropdown using its id ("RF25")
    dropdown = WebDriverWait(driver, 100).until(
        ec.visibility_of_element_located((By.ID, dropdown_id))
    )

    # Create a Select object to interact with the dropdown
    select_year = Select(dropdown)

    # Loop through each year as required
    for year in range(start, end):
        # Select year from the dropdown
        select_year.select_by_value(str(year))  # Using 'value' attribute

        # Wait for the "Download" button to be clickable
        download_button = WebDriverWait(driver, 100).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input.btn.btn-success[type='submit'][value='Download']"))
        )

        time.sleep(2)
        # Click the "Download" button
        download_button.click()

    # Wait for downloads to finish before quitting
    wait_for_downloads(download_dir)
    time.sleep(5)
    driver.quit()

# Function to download Gridded Data Real Time
def realtime_download(start, end, box_id, download_id, webpage, rename_files=False):
    chrome_launch(webpage=webpage)

    start_date = datetime(start, 1, 1)
    end_date = datetime(end, 12, 31)
    current_date = start_date
    while current_date <= end_date:
        condensed_date = current_date.strftime('%d%m%Y')

        # Check if file is already downloaded
        download = True
        if os.listdir(download_dir):
            for existing_file in os.listdir(download_dir):
                match_1 = re.search(r"(\d{4})\+(\d{1,2})\+(\d{1,2})", existing_file)
                match_2 = re.search(r"_(\d{2})_(\d{2})_(\d{2})", existing_file)
                if match_1:
                    year, month, day = map(int, match_1.groups())
                    date_str = f"{day:02d}{month:02d}{year:04d}"
                elif match_2:
                    day, month, year = map(int, match_2.groups())
                    year += 2000
                    date_str = f"{day:02d}{month:02d}{year:04d}"
                else:
                    print(f"Check whether {existing_file} is a valid file")
                    date_str = None

                if date_str == condensed_date:
                    download = False
                    print(f"{existing_file} already downloaded")
                    break

        # Download if necessary
        if download:
            # Input date into the box
            search = WebDriverWait(driver, 3600).until(
                ec.presence_of_element_located((By.ID, box_id))
            )
            search.clear()
            search.send_keys(condensed_date)

            # Wait till the dates are visible
            WebDriverWait(driver, 3600).until(
            ec.text_to_be_present_in_element_value((By.ID, box_id), condensed_date)
            )

            # Click the download button
            download_button = driver.find_element(By.CSS_SELECTOR, download_id)
            download_button.click()

            # Renaming files if necessary
            if rename_files:
                wait_for_downloads(download_dir)
                time.sleep(2)
                for downloaded_file in os.listdir(download_dir):
                    old_name_path = os.path.join(download_dir, downloaded_file)
                    new_name = f"{var}-{var_type}-{current_date.year}+{current_date.month}+{current_date.day}.grd"
                    new_name_path = os.path.join(download_dir, new_name)
                    # Does not touch the files that are already renamed
                    if not os.path.exists(new_name_path):
                        os.rename(old_name_path, new_name_path)
                    # Checks whether renaming is complete
                    while not os.path.exists(new_name_path):
                        print(f"Waiting for file to be renamed to: {new_name}")
                        time.sleep(1)
        # Iteration
        current_date += timedelta(days=1)
    wait_for_downloads(download_dir)
    driver.quit()

# Preparing the download directory for IMD data for the given variable
dir_path = output_folder + r"\{0}-{1}".format(var, var_type)
download_dir = dir_path
os.makedirs(download_dir, exist_ok=True)

# Download according to the variable and variable type
if var_type == 'archive':
    if var == 'rainNC':
        IMD_webpage = 'https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html'
        archive_download(start=start_year, end=end_year+1, dropdown_id="RF25", webpage=IMD_webpage)
    elif var == 'rainBIN':
        IMD_webpage = 'https://www.imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html'
        archive_download(start=start_year, end=end_year+1, dropdown_id="rain", webpage=IMD_webpage)
    elif var == 'temp_max':
        IMD_webpage = 'https://imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html'
        archive_download(start=start_year, end=end_year+1, dropdown_id="maxtemp", webpage=IMD_webpage)
    elif var == 'temp_min':
        IMD_webpage = 'https://imdpune.gov.in/cmpg/Griddata/Min_1_Bin.html'
        archive_download(start=start_year, end=end_year+1, dropdown_id="mintemp", webpage=IMD_webpage)
    else:
        print("Please check description for IMD variables available for archive data (line 21)")
        os.rmdir(download_dir)
elif var_type == 'realtime':
    if var == 'rainNC':
        print("netCDF files for rainfall are not available in Gridded Data Real Time database.\n"
              "Try 'rainBIN' for binary data instead")
        os.rmdir(download_dir)
    elif var == 'rainBIN':
        IMD_webpage = 'https://www.imdpune.gov.in/cmpg/Realtimedata/Rainfall/Rain_Download.html'
        realtime_download(start_year, end_year, 'rain', '.btn.btn-success', webpage=IMD_webpage)
    elif var == 'temp_max':
        IMD_webpage = 'https://www.imdpune.gov.in/cmpg/Realtimedata/max/Max_Download.html'
        realtime_download(
            start_year, end_year, 'max', '.btn.btn-warning', webpage=IMD_webpage, rename_files=True
        )
    elif var == 'temp_min':
        IMD_webpage = 'https://www.imdpune.gov.in/cmpg/Realtimedata/min/Min_Download.html'
        realtime_download(
            start_year, end_year, 'min', '.btn.btn-info', webpage=IMD_webpage, rename_files=True
        )
    else:
        print("Please check description for IMD variables available for realtime data (line 21)")
        os.rmdir(download_dir)
else:
    print('Please check valid variable types (line 18).')
    os.rmdir(download_dir)
