# 
# Generates data files for a single country
# 

import os
import re
import numpy as np
import pandas as pd
from datetime import datetime


def sumarise_column(col):
    if np.issubdtype(col, np.number):
        if col.name in ['Confirmed', 'Deaths', 'Recovered', 'Active']:
            return col.sum()
        else:
            return col.mean()
    else:
        return list(col.values)[0]


def generate_location_df(input_dir, location_key, sum_country=False):
    """Generate country-specific df from directory with date-wise
    csv files containing internationally collated data.
    """
    country_df = pd.DataFrame()
    for file in os.listdir(input_dir):
        if not file.endswith(".csv"):
            continue
        df = pd.read_csv(input_dir + file)
        if sum_country:
            country_code = list(set(["Country_Region", "Country/Region"]) & set(df.columns.values))[0]
            rows = df[df[country_code] == location_key]
            row = pd.DataFrame(rows.apply(sumarise_column)).transpose()

        else:
            try:
                row = df.loc[df["Combined_Key"] == location_key].copy()
            except KeyError:
                if "Province_State" in df.columns.values:
                    row = df.loc[df["Province_State"] == location_key].copy()
                else:
                    continue

        row["Date"] = datetime.strptime(file.split(".")[0], '%m-%d-%Y')
        country_df = pd.concat(pd.Series([country_df, row]), axis=0)

    # Resolve naming inconsistencies in data
    try:
        country_df['Incident_Rate'] = country_df['Incident_Rate'].fillna(country_df['Incidence_Rate'])
        country_df['Case_Fatality_Ratio'] = country_df['Case_Fatality_Ratio'].fillna(country_df['Case-Fatality_Ratio'])
        country_df.drop(['Incidence_Rate', 'Case-Fatality_Ratio'], axis=1, inplace=True)
    except KeyError:
        pass
    country_df.dropna(how='all', axis=1, inplace=True)

    return country_df

def generate_all_df(input_dir, output_dir, countries_only = False, overwrite_files = False):
    """Generates location specific files for all locations found in the
    first valid file in the directory."""
    search_index = 0
    while True:
        initial_file = os.listdir(input_dir)[search_index]
        df = pd.read_csv(input_dir + initial_file)
        if countries_only and "Country_Region" in df.columns:
            locations = df["Country_Region"].unique()
        elif "Combined_Key" in df.columns:
            locations = df["Combined_Key"].unique()
        elif "Province_State" in df.columns:
            locations = df["Province_State"].unique()
        else:
            search_index += 1
            continue
        break
    
    for location in locations:
        output_name = output_dir + re.sub('\W+', '', location) + ".csv"
        if os.path.isfile(output_name) and not overwrite_files:
            continue
        country_df = generate_location_df(input_dir, location, countries_only)
        country_df.to_csv(output_name)

def rel_reporting_calc(df, column_list):
    """Adds columns to dataframe giving weekday information,
    as well as the relative reporting factor."""
    df['Day_Index'] = df['Date'].apply(lambda x: x.weekday())
    df['Weekday'] = df['Date'].apply(lambda x: x.day_name())
    for column in column_list:
        mean = df[column].rolling(7).mean()
        df['Dif_' + column] = df[column] / mean
    return df       


input_dir = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
output_dir = "data/"
location_key = "England, United Kingdom"

if __name__ == '__main__':
    # country_df = generate_location_df(input_dir, location_key)
    # country_df.to_csv(output_dir + re.sub('\W+','',location_key) + ".csv")

    input_dir = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
    output_dir = "data/country_data/"

    generate_all_df(input_dir, output_dir, overwrite_files=False, countries_only=True)