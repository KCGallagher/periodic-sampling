#
# Code to access Public Health England (PHE) Covid-19 data. via the public API
# Based on code by Donald Hernik (Dec 2020) - Overload, 28(160):10-12,
# Available at https://accu.org/journals/overload/28/160/hernik/
#

import pandas as pd
from uk_covid19 import Cov19API

def retrieve_data(area_name, area_type):
  """Get the Covid data via the API"""
  try:  
    location_filter = [f'areaType={area_type}',
    f'areaName={area_name}']

    # The metric(s) to request
    req_structure = {
        "date": "date",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
        "newDeaths28DaysByDeathDate": "newDeaths28DaysByDeathDate",
        "newDeaths28DaysByPublishDate": "newDeaths28DaysByPublishDate",
        "newVirusTestsBySpecimenDate": "newVirusTestsBySpecimenDate"
    }

    api = Cov19API(filters=location_filter, structure=req_structure)

    data = api.get_json()
    return data['data']

  except Exception as ex: # pylint: disable=broad-except
    print(f'Exception [{ex}]')


if __name__ == "__main__":
    data = retrieve_data(area_name='england', area_type='nation')
    pd.DataFrame(data).to_csv("UK_raw_data/uk_data.csv")
