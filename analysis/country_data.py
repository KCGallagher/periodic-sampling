# 
# Generates data files for a single country
# 

import os
import re
import pandas as pd
from datetime import datetime


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
            if "Province_State" in df.columns.values:
                row = df.loc[df["Province_State"] == location_key].copy()
            else:
                continue

        row["Date"] = datetime.strptime(file.split(".")[0], '%m-%d-%Y')
        country_df = pd.concat([country_df, row])

    # Resolve naming inconsistencies in data
    try:
        country_df['Incident_Rate'] = country_df['Incident_Rate'].fillna(country_df['Incidence_Rate'])
        country_df['Case_Fatality_Ratio'] = country_df['Case_Fatality_Ratio'].fillna(country_df['Case-Fatality_Ratio'])
        country_df.drop(['Incidence_Rate', 'Case-Fatality_Ratio'], axis=1, inplace=True)
    except KeyError:
        pass
    country_df.dropna(how='all', axis=1, inplace=True)

    return country_df


input_dir = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
output_dir = "data/"
location_key = "England, United Kingdom"

if __name__ == '__main__':
    country_df = generate_location_df(input_dir, location_key)
    country_df.to_csv(output_dir + re.sub('\W+','',location_key) + ".csv")