"""
Our first python script is `download_sec_zips.py`, which downloads SEC zip files to a local directory titled `sec_zips`. This will allow the following scripts to parse and combine the data.
"""

import zipfile
import os 
import re  
imort pandas as pd  

def process_zip_files(local_zip_dir="sec_zips", output_csv="notebook1_insider_data.csv"):
    """
    This function processes ZIP files in the specified directory, extracting relevant TSV files for further analysis.
    """
    # In order to concatenate all files in order, we can sort this list
    all_files = sorted([f for f in os.listdir(local_zip_dir) if f.endswith(".zip")])
    print(f"Found {len(all_files)} ZIP files in '{local_zip_dir}', starting from: {all_files[0]} and ending with: {all_files[-1]}")

    # Let's create a list to store the columns that we want for use in final_df and filtered_entities
    selected_columns = [
        "RPTOWNERNAME",
        "RPTOWNER_TITLE",
        "Insider Role",
        "ISSUERNAME",
        "ISSUERTRADINGSYMBOL",
        "ISSUERCIK",
        "PERIOD_OF_REPORT",
        "TRANS_DATE",
        "SECURITY_TITLE",
        "TRANS_CODE",
        "TRANS_SHARES",
        "TRANS_PRICEPERSHARE",
        "SHRS_OWND_FOLWNG_TRANS",
        "DIRECT_INDIRECT_OWNERSHIP",
        "ACCESSION_NUMBER",
    ]
    
    renaming_dict = {
        "RPTOWNERNAME": "Insider Name",
        "RPTOWNER_TITLE": "Insider Title",
        "Insider Role": "Insider Role",
        "ISSUERNAME": "Issuer",
        "ISSUERTRADINGSYMBOL": "Ticker",
        "ISSUERCIK": "CIK Code",
        "PERIOD_OF_REPORT": "Period of Report",
        "TRANS_DATE": "Transaction Date",
        "SECURITY_TITLE": "Security",
        "TRANS_CODE": "Transaction Code",
        "TRANS_SHARES": "Shares",
        "TRANS_PRICEPERSHARE": "Price per Share",
        "SHRS_OWND_FOLWNG_TRANS": "Shares After",
        "DIRECT_INDIRECT_OWNERSHIP": "Ownership Type",
    }
    
    # Loop through each ZIP file
    for zip_filename in all_files:
        """
        Design a function to loop through each ZIP file in the local directory and extract the relevant TSV files for processing.
        """
        print(f"Processing file: {zip_filename}")
        # Contruct the full path to the ZIP file
        zip_path = os.path.join(local_zip_dir, zip_filename)
        # Create a folder name by dropping the ".zip" extension
        folder_name = zip_filename.replace(".zip", "")
        # Create a folder to extract the contents of the ZIP file
        extract_path = f"{local_zip_dir}/{folder_name}"
    
        # Extract the ZIP files but use an elegant Try/Except block to handle errors
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
        except Exception as e:
            print(f"Skipping {zip_filename} due to extraction error: {e}")
            continue
    
        # Now that we have extracted the ZIP file, let's find the TSV files we want in the extracted folder
        try:
            nonderiv = pd.read_csv(
                os.path.join(extract_path, "NONDERIV_TRANS.tsv"), sep="\t", low_memory=False
            )  # used to suppress dtype warning
            report = pd.read_csv(os.path.join(extract_path, "REPORTINGOWNER.tsv"), sep="\t")
            submission = pd.read_csv(os.path.join(extract_path, "SUBMISSION.tsv"), sep="\t")
        except Exception as e:
            print(f"Skipping {zip_filename} due to load error: {e}")
            continue
    
        # In the original notebook we had a function get_role() which did not work, so this replaces it with a simpler approach
        report["Insider Role"] = report["RPTOWNER_RELATIONSHIP"].str.strip().str.title()
    
        # Now let's filter the non-deriv file for open-market buys "P" we can include Sales in the future "S""Insider Trading_ Do Corporate Insiders Know Something We Don't_.docx"
        filtered = nonderiv[
            (nonderiv["SECURITY_TITLE"].str.lower() == "common stock")
            & (nonderiv["TRANS_CODE"] == "P")
        ]
    
        # Let's also filter out any "penny stocks" in this case we will say any with a share price < $5
        filtered = filtered[filtered["TRANS_PRICEPERSHARE"] >= 5.0].copy()
    
        # Here we are going to use a merge statement to join the filtered and the report data that we want
        filtered = filtered.merge(
            report[
                [
                    "ACCESSION_NUMBER",
                    "RPTOWNERNAME",
                    "RPTOWNER_TITLE",
                    "RPTOWNER_RELATIONSHIP",
                    "Insider Role",
                ]
            ],
            on="ACCESSION_NUMBER",
            how="left",
        )
    
        # Now, let's create a copy to work on incase we mess anything up it will be easy to redo
        before_entity_filter = filtered.copy()
    
        # Let's convert the 'RPTOWNERNAME' to all uppercase for ease
        filtered["RPTOWNERNAME"] = filtered["RPTOWNERNAME"].str.upper()
    
        # Let's also create a list of entity_keywords that we want to search for
        entity_keywords = [
            "LLC",
            "L L C",
            "L.L.C.",
            "LP",
            "L P",
            "L.P.",
            "LTD",
            "INC",
            "TRUST",
            "CORP",
            "FOUNDATION",
            "COMPANY",
            "CO",
            "CO.",
            "PARTNERS",
            "ADVISORS",
            "ADVISORY",
            "CAPITAL",
            "INVESTMENT",
            "INVESTMENTS",
            "HOLDINGS",
            "MGMT",
            "MANAGEMENT",
            "FUND",
            "GROUP",
            "VENTURES",
            "BIOVENTURES",
            "INVESTORS",
            "EQUITY",
            "LIFE INSURANCE",
            "GP",
            "FAMILY",
            "PBC",
            "SDN BHD",
            "GMBH",
        ]
    
        # Now, let's create a regex pattern that detects keywordse with leading punctuation or spacing (to avoid names)
        # For a full description of what this pattern does see `explanation of regex in Notebook2.docx`
        pattern = "(?i)" + "|".join(
            r"(?<!\w)" + re.escape(k) + r"(?=\W|$)" for k in entity_keywords
        )
    
        # Save the rows that will be the filtered out entities (for later review)
        # filtered_out_df = before_entity_filter[before_entity_filter["RPTOWNERNAME"].str.contains(pattern, case=False, na=False, regex=True)].copy()
    
        # Merge the entity-filtered-out rows with submission info to align with final_df format
        # filtered_out_df = filtered_out_df.merge(
        #    submission[["ACCESSION_NUMBER", "ISSUERNAME", "ISSUERTRADINGSYMBOL", "PERIOD_OF_REPORT", "ISSUERCIK"]],
        #    on="ACCESSION_NUMBER", how="left"
        # )
    
        # Remove rows where the insider name matches any known entity keyword (e.g., LLC, INC, TRUST)
        # Uses word boundaries to avoid false positives
        filtered = filtered[
            ~filtered["RPTOWNERNAME"].str.contains(
                pattern, case=False, na=False, regex=True
            )
        ]
    
        # Keep only valid insiders: director, officer, or has a job title, I may consider removing this line in the future
        # .loc[;, ] used to address warning (means assign this transformation to every row in the column)
        filtered.loc[:, "RPTOWNER_RELATIONSHIP"] = filtered[
            "RPTOWNER_RELATIONSHIP"
        ].str.upper()
        filtered = filtered[
            filtered["RPTOWNER_RELATIONSHIP"].str.contains(
                "DIRECTOR|OFFICER|TENPERCENTOWNER", na=False
            )
            | filtered["RPTOWNER_TITLE"].notna()
        ]
    
        # Merge with submission to get equity issuer info
        filtered = filtered.merge(
            submission[
                [
                    "ACCESSION_NUMBER",
                    "ISSUERNAME",
                    "ISSUERTRADINGSYMBOL",
                    "PERIOD_OF_REPORT",
                    "ISSUERCIK",  # Added "ISSUECIK" to map this field with SIC code
                ]
            ],
            on="ACCESSION_NUMBER",
            how="left",
        )
    
        # Filter out equity issuers that are investment funds
        filtered = filtered[
            ~filtered["ISSUERNAME"].str.contains("FUND", case=False, na=False)
            & ~filtered["ISSUERNAME"].str.contains("trust", case=False, na=False)
        ]
    
        # Now we can rename output columns using our dictionary from earlier
        final = filtered[selected_columns].rename(columns=renaming_dict)
    
        # Append cleaned dataframe to master list
        merged_all.append(final)

        # Combine all cleaned rows into one DataFrame
    if merged_all:
        final_df = pd.concat(merged_all, ignore_index=True)
    
        # Save merged data
        final_df.to_csv("notebook1_insider_data.csv", index=False)
        print("Saved merged data to notebook1_insider_data.csv")
        print(f"New CSV file contains {final_df.shape[0]} entries and {final_df.shape[1]} features")
    
        # Preview output
        print("Preview of merged data:")
        pd.set_option('display.max_columns', None)
        display(final_df.head(10))
        
    else:
        print("No valid purchase data found in uploaded zip files.")
    
if __name__ == "__main__":
    process_zip_files()
    print("Processing complete.")