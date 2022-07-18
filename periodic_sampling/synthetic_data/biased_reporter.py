#
# Class to report case data with periodic biases
#

import math
import numpy as np
from datetime import datetime, timedelta


class Reporter():
    """Reporter class for epidemiological case data,
    including biased reporters to replicate periodic
    trends in real data."""

    def __init__(self, case_data, start_date='01/01/2020', fatality_rate=0.02) -> None:
        """Instatinate with case data dataframe.
        
        Parameters
        ----------
        case_data : pd.Dataframe
            At minimum, contains case data indexed by day
        start_date : str
            Date of initial infection, in the form 'DD/MM/YYYY'
        fatality_rate : float
            Optional factor to convert cases to deaths by uniform factor - 
            this functionality is a placeholder and is not accurate
        """

        self.case_data = case_data
        self.start_date = datetime.strptime(start_date, "%d/%m/%Y").date()
        self.fatality_rate = fatality_rate

    def unbiased_report(self, output_path, df = None):
        """Save data to .csv format at 'output_loc' compatible with
        John Hopkins Covid Data, without modifying data"""
        if df is None:
            df = self.case_data.copy()
        df['Date'] = df.apply(lambda row: self.start_date 
                                    + timedelta(days=int(row.name)), axis=1)
        df['Combined_Key'] = 'Synthetic Data'
        
        if 'Confirmed' not in self.case_data.columns:
            df.rename(columns={'Cases': 'Confirmed'}, inplace=True)
        df['Deaths'] = df['Confirmed'].apply(lambda x: math.floor(x * self.fatality_rate
                                                                  + np.random.uniform()))
        df.to_csv(output_path)