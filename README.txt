README.txt

===========================================
Insider Transactions Analysis (2006–2025)
===========================================

Project Title
-------------
Insider Trading: *Do Corporate Insiders Know Something We Don't?*  
(See: `Insider Trading: Do Corporate Insiders Know Something We Don't?.docx' Project Proposal)

Note: This github repository has been forked from our original project so that I, Thomas MacPherson, can clean up some code 
and continue with the exploration and analysis of the data. 

To see the original github repository please visit: https://github.com/RamiHaider/Do-Insiders-Know-Something-We-Dont

Project Overview
----------------
This project builds a comprehensive dataset of insider transactions from **Q1 2006 through Q1 2025**, extracted from **SEC Form 4 filings**. It analyzes insider buying and selling patterns, combines this data with stock price history, and evaluates the predictive power of insider activity.

We extract key details from Form 4 filings, including:
- Insider Name
- Title
- Role (e.g., Officer, Director, 10% Owner)
- Issuer Name
- Ticker Symbol
- CIK Code
- Period of Report
- Transaction Date
- Security Type (e.g., Common Stock, Derivative)
- Transaction Code (P = Purchase, S = Sale, etc.)
- Ownership Type (Direct/Indirect)
- Accession Number
- Number of Shares
- Price per Share
- Shares Held After Transaction

Refer to `insider_transaction_readme.pdf` for a full explanation of Form 4 fields and how this information is structured.

A copy of the SEC zip files can be found in the directory titled sec_zips

---

Market Data Integration
-----------------------
Using `yfinance`, we supplement SEC insider transaction data with:
- **Historical stock prices** before and after each transaction (T-1M, T0, T+1M to T+6M)
- **28-period moving average trends** for each period
- **Issuer metadata** including market cap, sector, and industry classification, etc.

This enables long-horizon return analysis and factor-adjusted performance evaluation of insider trades.

---

Jupyter Notebooks
-----------------
Pre. **`Virtual_Environment_Setup.ipynb`**
   Instructions on setting up a virtual environment that contains all libraries and dependencies need to run this project.

1. **`Notebook 1 - download_sec_zips.ipynb`**  
   Downloads raw SEC Form 4 zip files from EDGAR (Q1 2006 – Q1 2025) and saves them to a new directory 'sec_zips' in the current working directory.

2. **`Notebook 2 - insiders_zip_data_processing.ipynb`**  
   Parses files from 77 zip archives and extracts structured insider transaction data.  
   Refer to: `Explanation of Regex in Notebook 2.docx` for regex logic.  
   Output: `notebook1_insider_data.csv` - Main CSV
           `notebook1_filtered_out_entities.csv` - Records or future use CSV

3. **`Notebook 3 - yahoo_finance_price_data.ipynb`**  
   Uses the insider data from Notebook 2 to query Yahoo Finance. Retrieves prices and 28-period moving averages across pre- and post-transaction windows.  
   Output: `notebook3_added_price_data.csv`

4. **`Notebook 4 - Market_Cap_Sector_Industry_Classification.ipynb`**  
   Adds market cap, sector, industry and other corporate information using `yfinance`.
   Output: `notebook4_enhanced_corporate_info.csv`

5. **`Notebook 5 - Thomas_EDA.ipynb`**  
   Performs data cleaning, exploratory data analysis (EDA), and statistical tests to identify patterns and significant anomalies in insider trading behavior.
   Output: `notebook5_cleaned_titles.csv`

6. **`Notebook 6 - good_buyers.ipynb`**
   Filters out good and bad buyers based on broad market returns including beta adjusted returns.
   Output: `notebook6_data.csv`
          
> Additional notebooks may be added as the analysis and modeling evolves.

---

CSV Outputs
-----------
- `notebook1_insider_data.csv`  
  Clean, structured insider transactions parsed from SEC Form 4 filings. This is our main CSV moving forward.

- `notebook1_filtered_out_entities.csv`  
  Investment entities and non-corporate issuers filtered out from the main dataset. This is kept for our records or future use.

- `notebook3_added_price_data.csv`  
  Insider transaction data augmented with pre- and post-transaction price and trend data.

- `notebook4_enhanced_corporate_info.csv`
  Inisder transaction data augmented with price, trend and corporate information.

- `notebook5_cleaned_titles`
  Insider titles have been manually cleaned, normalized, then encoded using dummy variables for easy analysis.

- `notebook6_data.csv`  
  Dataset used to find insiders who significantly **outperformed** the market after adjusting for stock volatility.

---

Role Abbreviations in Notebook 5
---------------------------------
Notebook 5 contains a comprehensive mapping of insider titles and roles. Here is a subset (see full notebook for details):

- CEO: Chief Executive Officer
- CFO: Chief Financial Officer
- COO: Chief Operating Officer
- CTO: Chief Technology Officer
- CMO: Chief Marketing Officer
- CSO: Chief Strategy Officer
- EVP / SVP / VP: Executive, Senior, and Vice Presidents
- P / Pc / Pi / Pf: President (and variants)
- D / C / VC: Director, Chairman, Vice Chairman
- F: Founder
- GC: General Counsel
- S: Corporate Secretary
- T: Treasurer
- ...and many others including Heads of Divisions, Managing Directors, and Department Leaders.

> These are used to categorize insiders and explore patterns in trades across different leadership roles.

For a full list of abbreviations see Notebook 5 - Thomas_EDA.ipynb
---

Environment Setup
-----------------
You can install project dependencies using **either Conda or pip**, depending on your preference:

See `Virtual_Environment_Setup.ipynb` for instructions on setting up virtual environments specific for the Insider Trading Project