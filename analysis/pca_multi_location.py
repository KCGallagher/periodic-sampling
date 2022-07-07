#
# Conducts principal component analysis, across data from different locations
#

import os
import numpy as np
import pandas as pd

from country_data import generate_all_df, rel_reporting_calc


input_dir = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us/"
output_dir = "data/us_states/"
test_dir = "data/uk_test/"


def generate_pca_array(search_dir, column):
    """Each row in the array corresponds to a single location,
    and has 7 elements representing the average reporting factor
    on each day of the week. The method of averaging can be specificied,
    but defaults to the median (to avoid bias from extremes.
    
    Column is either 'Cases' or 'Deaths'."""
    pca_array = []
    for file in os.listdir(search_dir):
        initial_df = pd.read_csv(search_dir + file)
        initial_df["Date"] = pd.to_datetime(initial_df["Date"], format = "%Y-%m-%d")
        initial_df.sort_values(by="Date", inplace=True)
        row = average_reporting_factor(initial_df, column)
        if (np.any(np.isnan(row)) or (np.sum(row) <= 0)):
            continue
        pca_array.append(row)
    return np.asarray(pca_array)

def average_reporting_factor(df, column):
    """Average reporting factor per weekday for a specified column."""
    df["Daily_Deaths"] = df["Deaths"].diff()
    df["Daily_Cases"] = df["Confirmed"].diff()
    df[["Daily_Deaths","Daily_Cases"]] = df[["Daily_Deaths","Daily_Cases"]].clip(lower = 0)

    df = rel_reporting_calc(df, ['Daily_Cases', 'Daily_Deaths'])
    summary = df.groupby('Weekday').mean().sort_values('Day_Index')
    return list(summary['Dif_Daily_' + column].values)

def test_normalisation(arr, rtol):
    """Tests whether reporting factors across a week average to
    unity, within a specified relative tolerance."""
    sums = np.sum(arr, axis=1) / 7
    agreement = np.isclose(sums, 1, rtol=rtol, atol=0)
    failures = np.sum(np.invert(agreement))
    print(f"There were {failures} rows out of tolerance.")


if __name__ == '__main__':
    generate_all_df(input_dir, output_dir, overwrite_files=False)
    pca_array = generate_pca_array(output_dir, 'Cases')
    test_normalisation(pca_array, rtol=0.05)
