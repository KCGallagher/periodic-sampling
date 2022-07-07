#
# Conducts principal component analysis, primarily on US state data
#

import os
import re
import pandas as pd

from country_data import generate_location_df


input_dir = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us/"
output_dir = "data/us_states/"

def generate_all_df(input_dir, output_dif):
    """Generates location specific files for all locations found in the
    first valid file in the directory."""
    search_index = 0
    while True:
        initial_file = os.listdir(input_dir)[search_index]
        df = pd.read_csv(input_dir + initial_file)
        if "Combined_Key" in df.columns:
            locations = df["Combined_Key"].unique()
        elif "Province_State" in df.columns:
            locations = df["Province_State"].unique()
        else:
            search_index += 1
            continue
        break

    for location in locations:
        country_df = generate_location_df(input_dir, location)
        country_df.to_csv(output_dir + re.sub('\W+','',location) + ".csv")
    

if __name__ == '__main__':
    generate_all_df(input_dir, output_dir)
