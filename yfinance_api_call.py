"""
Third notebook in our series of data aggregation for analiss of insider trading. This notebook will query yahoo finance for stock data and then use this data to update the CSV file that we are using to store our data.
"""

import os
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import date
