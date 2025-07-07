"""
Third notebook in our series of data aggregation for analiss of insider
trading. This notebook will query yahoo finance for stock data and then use
this data to update the CSV file that we are using to store our data.
"""

from datetime import date
import numpy as np
import pandas as pd
import yfinance as yf


# Let's create a function to clean up data and visualize some information
def read_data(file_path):
    """
    Bring in our previous file in order to add new price data to it.
    """
    # Read in the .csv file
    cs_df = pd.read_csv(file_path)
    print(f"Let's take a look at the size of our dataframe: {cs_df.shape}\n")
    # print(cs_df.head())

    # Let's start by removing any data where tickers == None
    cs_df = cs_df[cs_df["Ticker"] != "NONE"]
    cs_df = cs_df[cs_df["Ticker"] != "None"]

    # Let's also drop any column that is missing the ticker or the price per
    # share or any shares purchased
    cs_df = cs_df[~cs_df["Ticker"].isna()].copy()
    cs_df = cs_df[~cs_df["Price per Share"].isna()].copy()
    cs_df = cs_df[cs_df["Shares"] > 0.0]

    # Let's fill missing insider titles, names and issuers with a string for
    # the group by statement
    cs_df[["Insider Title", "Insider Name", "Issuer"]] = cs_df[
        ["Insider Title", "Insider Name", "Issuer"]
    ].fillna("Missing")
    print(f"After removing transction with no tickers we have {cs_df.shape}\n")

    # Let's take a look at the number of unique tickers in this file
    tickers = list(cs_df["Ticker"].unique())
    print(f"We have {len(tickers)} unique tickers\n")

    # We can actually delete this tickers list and set it up as a generator to
    # be more memory efficient for our loop
    del tickers
    tickers = (sym for sym in cs_df["Ticker"].unique())

    # Let's take a look at the number of missing values in the file
    missing_counts = cs_df.isna().sum()
    print(missing_counts)

    return cs_df, tickers


def daily_transactions(df: pd.DataFrame):
    """
    Takes a dataframe and calculates the total capital invested for the
    transaction. All data is then aggregated based on characteristics like
    name, title, date, etc. The average price per share is calculated for the
    transaction date and a grouped dataframe is returned.
    """

    # Let's calcualte the capital invested for each individual transaction
    df["total_capital"] = df["Shares"] * df["Price per Share"]

    # Let's group the dataframe so that we get all transactions on the same day
    # by the same insider as a single transaction
    grouped_df = df.groupby(
        [
            "Insider Name",
            "Insider Title",
            "Insider Role",
            "Issuer",
            "Ticker",
            "CIK Code",
            "Period of Report",
            "Transaction Date",
            "Security",
            "Transaction Code",
            "Ownership Type",
            "ACCESSION_NUMBER",
        ],
        as_index=False,
    ).agg(
        shares=("Shares", "sum"),
        price_per_share=("Price per Share", "mean"),
        shares_after=("Shares After", "max"),
        total_capital=("total_capital", "sum"),
    )
    # Now, we can find the average price per share
    grouped_df["average_price_per_share"] = (
        grouped_df["total_capital"] / grouped_df["shares"]
    )
    # print(grouped_df.shape)
    return grouped_df


def get_price_data(df, tickers):
    """
    Query the yfinance API to get the price data for each ticker in the
    dataframe. The data is then added to the original dataframe.
    """
    # Now we can use the ticker to request that complete historical data for
    # this ticker
    for ticker in tickers:
        try:
            # The first the we need to do is find all of the transactions with
            # this ticker
            print(f"\nProcsessing ticker {ticker}...")
            temp_df = df.loc[df["Ticker"] == ticker].copy()
            # Now that we have a temporary dataframe, we can pull the price data
            ticker_data = yf.download(
                tickers=ticker,
                period="max",
                interval="1d",
                auto_adjust=True,
                actions=False,
                threads=False,
            )
            # Let's calculate the moving avearge
            ticker_data["28MA"] = ticker_data["Close"].rolling(window=28).mean()
            # Let's normalize it based on the previous value of the MA
            ticker_data["MA_diff"] = ticker_data["28MA"].pct_change()
            ticker_data = ticker_data.dropna().copy()
            # Finally, I want to take the rolling average of that MA_diff
            # (momentum of momentum change) over the last 28 days so we get the
            # monthly trend
            ticker_data["MA_trend"] = ticker_data["MA_diff"].rolling(window=28).mean()
            ticker_data = ticker_data.dropna().copy()
            ticker_data.index = pd.to_datetime(ticker_data.index)
            # print(ticker_data.head())

            # Now, we will have to iterate through the rows to fill them out
            # individually
            for index, row in temp_df.iterrows():
                # This is where we will need to grab the values and the index
                # and populate the orginal dataframe (grouped_df) Find out the
                # date of the transaction (specify the format explicitly)
                trans_date = pd.to_datetime(row["Transaction Date"], format="%d-%b-%Y")
                # Let's start by defining all of our dates
                date_premonth = trans_date - pd.DateOffset(months=1)
                date_onemonth = trans_date + pd.DateOffset(months=1)
                date_twomonth = trans_date + pd.DateOffset(months=2)
                date_threemonth = trans_date + pd.DateOffset(months=3)
                date_fourmonth = trans_date + pd.DateOffset(months=4)
                date_fivemonth = trans_date + pd.DateOffset(months=5)
                date_sixmonth = trans_date + pd.DateOffset(months=6)

                # Let's Get all of the prices at the right timepoints we will
                # use .asof because we likely only have trading days
                price_premonth = float(ticker_data["Close"][ticker].asof(date_premonth))
                price_onemonth = float(ticker_data["Close"][ticker].asof(date_onemonth))
                price_twomonth = float(ticker_data["Close"][ticker].asof(date_twomonth))
                price_threemonth = float(
                    ticker_data["Close"][ticker].asof(date_threemonth)
                )
                price_fourmonth = float(
                    ticker_data["Close"][ticker].asof(date_fourmonth)
                )
                price_fivemonth = float(
                    ticker_data["Close"][ticker].asof(date_fivemonth)
                )
                price_sixmonth = float(ticker_data["Close"][ticker].asof(date_sixmonth))

                # print(f"The price is {price_premonth,price_onemonth,
                # price_twomonth,price_threemonth,price_fourmonth,
                # price_fivemonth,price_sixmonth}")

                # Let's bring in the high and low of the transaction date so we
                # can verify the buy price was on that day
                high_transactiondate = float(
                    ticker_data["High"][ticker].asof(trans_date)
                )
                low_transactiondate = float(ticker_data["Low"][ticker].asof(trans_date))
                # print(high_transactiondate,low_transactiondate)

                # Let's get the momentum of all the trends
                trend_premonth = ticker_data["MA_trend"].asof(date_premonth)
                trend_transactiondate = float(ticker_data["MA_trend"].asof(trans_date))
                trend_onemonth = float(ticker_data["MA_trend"].asof(date_onemonth))
                trend_twomonth = float(ticker_data["MA_trend"].asof(date_twomonth))
                trend_threemonth = float(ticker_data["MA_trend"].asof(date_threemonth))
                trend_fourmonth = float(ticker_data["MA_trend"].asof(date_fourmonth))
                trend_fivemonth = float(ticker_data["MA_trend"].asof(date_fivemonth))
                trend_sixmonth = float(ticker_data["MA_trend"].asof(date_sixmonth))

                # Grab todays date
                today = pd.to_datetime(date.today())

                # Let's see if we can change the original dataframe with these
                # new values (we will use .at because its faster and replaces
                # copies)

                df.at[index, "price_-1month"] = price_premonth
                df.at[index, "transactiondate_high"] = high_transactiondate
                df.at[index, "transactiondate_low"] = low_transactiondate

                if date_onemonth < today:
                    df.at[index, "price_1month"] = price_onemonth
                if date_twomonth < today:
                    df.at[index, "price_2month"] = price_twomonth
                if date_threemonth < today:
                    df.at[index, "price_3month"] = price_threemonth
                if date_fourmonth < today:
                    df.at[index, "price_4month"] = price_fourmonth
                if date_fivemonth < today:
                    df.at[index, "price_5month"] = price_fivemonth
                if date_sixmonth < today:
                    df.at[index, "price_6month"] = price_sixmonth

                # Let's add the price trend data as well
                df.at[index, "trend_-1month"] = trend_premonth
                df.at[index, "trend_transactiondate"] = trend_transactiondate
                if date_onemonth < today:
                    df.at[index, "trend_1month"] = trend_onemonth
                if date_twomonth < today:
                    df.at[index, "trend_2month"] = trend_twomonth
                if date_threemonth < today:
                    df.at[index, "trend_3month"] = trend_threemonth
                if date_fourmonth < today:
                    df.at[index, "trend_4month"] = trend_fourmonth
                if date_fivemonth < today:
                    df.at[index, "trend_5month"] = trend_fivemonth
                if date_sixmonth < today:
                    df.at[index, "trend_6month"] = trend_sixmonth

        except Exception as e:
            print(f"Failed to extract data for {ticker} from Yahoo Finance: {e}")

    return df


def removing_failed_tickers(df):
    """
    Remove any of the data that did not download properly from the yfinance API.
    """
    print(f"We originally had {grouped_df.shape[0]} rows")
    filtered_df = df[~df["price_-1month"].isna()]
    print(f"We were able to obtain data for {filtered_df.shape[0]} rows")
    uni_tick = filtered_df["Ticker"].unique()
    print(f"We now have {len(uni_tick)} unique tickers")
    print(f"We kept {np.round(len(uni_tick) / len(tickers) * 100, 1)}% of the tickers")

    return filtered_df


# Create a function to add columns to our dataframe
def add_columns(df, new_columns):
    """
    Prepare the datframe for new columns by adding them with NaN values.
    """
    for col in new_columns:
        df[col] = pd.NA
    return df


# Let's make a function to get spy data
def get_spy_data():
    """
    Query the yahoo finance API to get the SPY data for the appropriate time
    period.
    """
    # Let's get the spy dataframe and calculate the momentum of the trends
    ticker = "SPY"
    print(f"\nProcessing ticker {ticker}...")
    # Let's be sure to stay consistent with our ticker data calls
    spy_data = yf.download(
        tickers=ticker,
        period="max",
        interval="1d",
        auto_adjust=True,
        actions=False,
        threads=False,
    )
    # Let's calculate the moving averages
    spy_data["28MA"] = spy_data["Close"].rolling(window=28).mean()
    # Normalize it based on the previous days MA for comparisons
    spy_data["MA_diff"] = spy_data["28MA"].pct_change()
    # let's get rid of the first 29days because they dont have an MA_diff
    spy_data = spy_data.dropna().copy()
    # Finally, lets catch the monthly trend of this moving average
    spy_data["MA_trend"] = spy_data["MA_diff"].rolling(window=28).mean()
    # Let's drop the missing data again
    spy_data = spy_data.dropna().copy()
    # Let's explicitly make sure the date is in the proper format
    spy_data.index = pd.to_datetime(spy_data.index)
    return spy_data


# Let's create a function to merge the data
def merge_spy_data(df, spy_data, ticker):
    """
    Merge our dateframes together to get a working dataframe to export to a CSV
    file.
    """
    # Set up our looping function.
    for index, row in df.iterrows():
        # Find the original transaction data
        trans_date = pd.to_datetime(row["Transaction Date"])
        # Let's define all of the other dates we will look for in the spy_data
        date_premonth = trans_date - pd.DateOffset(months=1)
        date_onemonth = trans_date + pd.DateOffset(months=1)
        date_twomonth = trans_date + pd.DateOffset(months=2)
        date_threemonth = trans_date + pd.DateOffset(months=3)
        date_fourmonth = trans_date + pd.DateOffset(months=4)
        date_fivemonth = trans_date + pd.DateOffset(months=5)
        date_sixmonth = trans_date + pd.DateOffset(months=6)
        # Let's grab all of the price data from the spy_data. The initial data
        # is double indexed so use [ticker] to get access to the data
        price_premonth = np.round(spy_data["Close"][ticker].asof(date_premonth), 2)
        price_transactiondate = np.round(spy_data["Close"][ticker].asof(trans_date), 2)
        price_onemonth = np.round(spy_data["Close"][ticker].asof(date_onemonth), 2)
        price_twomonth = np.round(spy_data["Close"][ticker].asof(date_twomonth), 2)
        price_threemonth = np.round(spy_data["Close"][ticker].asof(date_threemonth), 2)
        price_fourmonth = np.round(spy_data["Close"][ticker].asof(date_fourmonth), 2)
        price_fivemonth = np.round(spy_data["Close"][ticker].asof(date_fivemonth), 2)
        price_sixmonth = np.round(spy_data["Close"][ticker].asof(date_sixmonth), 2)
        # print(price_premonth,price_transactiondate,price_sixmonth)
        # Let's get the momentum of all the trends
        trend_premonth = np.round(spy_data["MA_trend"].asof(date_premonth), 4)
        trend_transactiondate = np.round(spy_data["MA_trend"].asof(trans_date), 4)
        trend_onemonth = np.round(spy_data["MA_trend"].asof(date_onemonth), 4)
        trend_twomonth = np.round(spy_data["MA_trend"].asof(date_twomonth), 4)
        trend_threemonth = np.round(spy_data["MA_trend"].asof(date_threemonth), 4)
        trend_fourmonth = np.round(spy_data["MA_trend"].asof(date_fourmonth), 4)
        trend_fivemonth = np.round(spy_data["MA_trend"].asof(date_fivemonth), 4)
        trend_sixmonth = np.round(spy_data["MA_trend"].asof(date_sixmonth), 4)
        # print(trend_premonth,trend_transactiondate,trend_sixmonth)

        # Get todays date
        today = pd.to_datetime(date.today())

        # Let's update the original dataframe
        df.at[index, "spy_price_-1month"] = price_premonth
        df.at[index, "spy_price_transactiondate"] = price_transactiondate

        if date_onemonth < today:
            df.at[index, "spy_price_1month"] = price_onemonth
        if date_twomonth < today:
            df.at[index, "spy_price_2month"] = price_twomonth
        if date_threemonth < today:
            df.at[index, "spy_price_3month"] = price_threemonth
        if date_fourmonth < today:
            df.at[index, "spy_price_4month"] = price_fourmonth
        if date_fivemonth < today:
            df.at[index, "spy_price_5month"] = price_fivemonth
        if date_sixmonth < today:
            df.at[index, "spy_price_6month"] = price_sixmonth

        # Lets update the trend data
        df.at[index, "spy_trend_-1month"] = trend_premonth
        df.at[index, "spy_trend_transactiondate"] = trend_transactiondate
        if date_onemonth < today:
            df.at[index, "spy_trend_1month"] = trend_onemonth
        if date_twomonth < today:
            df.at[index, "spy_trend_2month"] = trend_twomonth
        if date_threemonth < today:
            df.at[index, "spy_trend_3month"] = trend_threemonth
        if date_fourmonth < today:
            df.at[index, "spy_trend_4month"] = trend_fourmonth
        if date_fivemonth < today:
            df.at[index, "spy_trend_5month"] = trend_fivemonth
        if date_sixmonth < today:
            df.at[index, "spy_trend_6month"] = trend_sixmonth

    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Current CSV file with insider data")
    parser.add_argument("output_file", help="New CSV file with added price data")
    args = parser.parse_args()

    cs_df, tickers = read_data(args.file_path)  # notebook1_insider_data.csv
    grouped_df = daily_transactions(cs_df)
    # Let's create a list of columns to add
    new_columns = [
        "price_-1month",
        "trend_-1month",
        "transactiondate_high",
        "transactiondate_low",
        "trend_transactiondate",
        "price_1month",
        "trend_1month",
        "price_2month",
        "trend_2month",
        "price_3month",
        "trend_3month",
        "price_4month",
        "trend_4month",
        "price_5month",
        "trend_5month",
        "price_6month",
        "trend_6month",
    ]
    grouped_df = add_columns(grouped_df, new_columns=new_columns)
    df = get_price_data(grouped_df, tickers)
    filtered_df = removing_failed_tickers(df)
    new_columns = [
        "spy_price_-1month",
        "spy_trend_-1month",
        "spy_price_transactiondate",
        "spy_trend_transactiondate",
        "spy_price_1month",
        "spy_trend_1month",
        "spy_price_2month",
        "spy_trend_2month",
        "spy_price_3month",
        "spy_trend_3month",
        "spy_price_4month",
        "spy_trend_4month",
        "spy_price_5month",
        "spy_trend_5month",
        "spy_price_6month",
        "spy_trend_6month",
    ]
    cs_df = add_columns(filtered_df, new_columns=new_columns)
    spy_data = get_spy_data()
    full_df = merge_spy_data(cs_df, spy_data, ticker="SPY")
    full_df.to_csv(args.output_file, index=False)  # notebook3_added_price_data.csv
