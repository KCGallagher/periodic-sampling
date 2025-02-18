#
# Conducts principal component analysis, across data from different locations
#

import os
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from country_data import generate_all_df, rel_reporting_calc


input_dir = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
output_dir = "data/country_data/"

def _generate_pca_row(search_dir, file, column):
    initial_df = pd.read_csv(search_dir + file)
    initial_df["Date"] = pd.to_datetime(initial_df["Date"], format = "%Y-%m-%d")
    initial_df.sort_values(by="Date", inplace=True)
    return average_reporting_factor(initial_df, column)

def generate_pca_array(search_dir, column):
    """Each row in the array corresponds to a single location,
    and has 7 elements representing the average reporting factor
    on each day of the week. The method of averaging can be specificied,
    but defaults to the median (to avoid bias from extremes.
    
    Column is either 'Cases' or 'Deaths'."""
    pca_array = []
    for file in os.listdir(search_dir):
        try:
            row = _generate_pca_row(search_dir, file, column)
        except KeyError:
            continue
        if (np.any(np.isnan(row)) or (np.sum(row) <= 0)):
            continue
        pca_array.append(row)
    return np.asarray(pca_array)

def generate_pca_df(search_dir, column):
    """Each row in the array corresponds to a single location,
    and has 7 elements representing the average reporting factor
    on each day of the week. The method of averaging can be specificied,
    but defaults to the median (to avoid bias from extremes.
    
    Column is either 'Cases' or 'Deaths'."""
    cols = ['Country', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    pca_df = pd.DataFrame(columns=cols)
    for file in os.listdir(search_dir):
        row = _generate_pca_row(search_dir, file, column)
        if (np.any(np.isnan(row)) or (np.sum(row) <= 0)):
            continue
        new_df = pd.DataFrame([[file.split('.')[0], *row]], columns=cols)
        pca_df = pd.concat([pca_df, new_df], axis=0)
    return pca_df

def average_reporting_factor(df, column):
    """Average reporting factor per weekday for a specified column."""
    df["Daily_Deaths"] = df["Deaths"].diff()
    df["Daily_Cases"] = df["Confirmed"].diff()
    df[["Daily_Deaths","Daily_Cases"]] = df[["Daily_Deaths","Daily_Cases"]].clip(lower = 0)

    df = rel_reporting_calc(df, ['Daily_Cases', 'Daily_Deaths'])
    summary = df.groupby('Weekday').mean().sort_values('Day_Index')
    # Mean required to ensure normalisation of summary - all values ave to 1
    return list(summary['Dif_Daily_' + column].values)

def test_normalisation(arr, rtol):
    """Tests whether reporting factors across a week average to
    unity, within a specified relative tolerance."""
    sums = np.sum(arr, axis=1) / 7
    agreement = np.isclose(sums, 1, rtol=rtol, atol=0)
    failures = np.sum(np.invert(agreement))
    print(f"There were {failures} rows out of tolerance.")

def run_pca(arr, n_components):
    """Runs Principal Component Analysis on input array."""
    arr = StandardScaler().fit_transform(arr)  # Normalisation
    pca_obj = PCA(n_components=n_components)
    pca_output = pca_obj.fit_transform(arr)
    print('Explained variation per principal component: '
          + str(pca_obj.explained_variance_ratio_))
    col_names = [('PC' + str(x + 1)) for x in range(n_components)]
    pca_df = pd.DataFrame(data=pca_output, columns=col_names,
                          index=['Mon', 'Tue', 'Wed', 'Thu', 'Fri',
                                 'Sat', 'Sun'])
    return pca_df

if __name__ == '__main__':
    # generate_all_df(input_dir, output_dir, overwrite_files=False)
    pca_array = generate_pca_array(output_dir, 'Cases')
    test_normalisation(pca_array, rtol=0.05)
    pca_df = run_pca(np.transpose(pca_array), n_components=2)
    print(pca_df.round(2))
