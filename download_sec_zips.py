"""
First python file in our pipleine that will access the SEC database and download
all of the Form 4 filings on record since 2006.
"""

import os
import requests
import pandas as pd


# Create main funciton to download SEC Form 4 ZIP files.
def download_sec_zips(save_dir: str = "sec_zips") -> None:
    """
    This is a function that will download SEC Form 4 ZIP files from the SEC website.

    Parameters:
    save_dir (str): The directory where the downloaded ZIP files will be saved.
                     Default is "sec_zips".
    output:
    This function will download all available SEC Form 4 ZIP files from 2006 to
    the current year and quarter.
    """

    # Create directory if it doesn't exist otherwise use existing directory.
    os.makedirs(save_dir, exist_ok=True)
    # The base URL for the SEC Form 4 data sets.
    base_url = (
        "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets"
    )

    # SEC blocks anonymous requests; requires a valid email.
    headers = {"User-Agent": "tmacphe@umich.edu"}

    # Create a list to keep track of any failed downloads
    failed = []

    # Let's get the current year and quarter so that we can get the most recent data
    now = pd.Timestamp.now()
    current_year = now.year
    quarter = now.quarter

    # Now that we have this, we can dynamically set the range of years and quarters to download.
    for year in range(2006, current_year + 1):
        for q in range(1, 5):
            if year == current_year and q >= quarter:
                break  # Only get files through the latest completed quarter.

            # Construct the filename and URL for each quarter so we can download the zip files.
            filename = f"{year}q{q}_form345.zip"
            url = f"{base_url}/{filename}"
            local_path = os.path.join(save_dir, filename)

            try:
                # Send a GET request to the URL to download the file.
                r = requests.get(url, headers=headers, timeout=30)
                # Check to see if the request was successful.(200 means successful download)
                if r.status_code == 200:
                    # Open file and then save to the local directory.
                    with open(local_path, "wb") as f:
                        f.write(r.content)
                    print(f"Downloaded: {filename}")
                else:
                    print(f"Failed: {filename} (status {r.status_code})")
                    failed.append(filename)
            # Handle any exceptions that occur during the download process.
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
                failed.append(filename)

    if failed:
        print("\nSome files failed to download:")
        for f in failed:
            print(" -", f)
    else:
        print("\nAll zip files downloaded successfully.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input", help="Save Directory for SEC Form 4 ZIP files", default="sec_zips"
    )
    args = parser.parse_args()

    download_sec_zips(save_dir=args.input)
