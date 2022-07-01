# 
# Generates data files for a single country
# 

import os
import re
import pandas as pd


def generate_location_df(input_dir, location_key):
    """Generate country-specific df from directory with date-wise
    csv files containing internationally collated data.
    """
    country_df = pd.DataFrame()
    for file in os.listdir(input_dir):
        if not file.endswith(".csv"):
            continue
        try:
            df = pd.read_csv(input_dir + file)
            row = df.loc[df["Combined_Key"] == location_key].copy()
        except KeyError:
            continue

        row["Date"] = file.split(".")[0]
        country_df = pd.concat([country_df, row])
    return country_df


input_dir = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
output_dir = "data/"
location_key = "England, United Kingdom"

if __name__ == '__main__':
    country_df = generate_location_df(input_dir, location_key)
    country_df.to_csv(output_dir + re.sub('\W+','',location_key) + ".csv")