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

        self.case_data['Date'] = self.case_data.apply(lambda row: self.start_date 
                                    + timedelta(days=int(row.name)), axis=1)

    def unbiased_report(self, output_path=None, df=None):
        """Save data to .csv format at 'output_path' compatible with
        John Hopkins Covid Data, without modifying case data.
        
        If output_path is not specified, return dataframe."""
        if df is None:
            df = self.case_data.copy()
        df['Combined_Key'] = 'Synthetic Data'
        
        if 'Confirmed' not in df.columns:
            df.rename(columns={'Cases': 'Confirmed'}, inplace=True)
        df['Deaths'] = df['Confirmed'].apply(lambda x: math.floor(x * self.fatality_rate
                                                                  + np.random.uniform()))
        if output_path is not None:
            df.to_csv(output_path)
        else:
            return df

    def fixed_bias_report(self, output_path=None, bias=None, multinomial_dist=False):
        """Adds a fixed weekly reporting bias to the case data. 
        Save data to .csv format at 'output_loc' compatible with
        John Hopkins Covid Data, without modifying data.

        Note: There may be slight discrepancies in total cases,
        due to rounding errors when scaling.
        
        Parameters
        ----------
        output_path : str
            Path to output csv with reported data
        bias : dict
            Dictionary mapping weekday names to reporting factors. 
            All values in the dictionary should average to unity,
            but normalisation will enforce this. Can also be passed
            as a list, where the first item corresponds to Monday.
        multinomial_dist : bool
            Boolean whether to reallocate cases based on a random multinomial
            distribution, or deterministically according to proportions provided
        """
        df = self.case_data.copy()

        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                    'Friday', 'Saturday', 'Sunday']
        df['Weekday'] = df['Date'].apply(lambda x: weekdays[x.weekday()])
        
        if bias is None:  # Default values from analysis
            bias = [1.3, 1.2, 1, 1, 1, 0.9, 0.6]
        if isinstance(bias, list):
            assert len(bias) == 7, 'Expected seven values for weekday bias'
            temp_dict = {}
            for i, value in enumerate(bias):
                temp_dict[weekdays[i]] = value
                bias = temp_dict  # Can now overwrite list values
        elif isinstance(bias, dict):
            assert set(weekdays) == set(bias.keys), 'Keys must match weekdays'

        normalisation = sum(bias.values())
        for v in bias.values():
            v /= normalisation

        if multinomial_dist:
            df['Confirmed'] = self.rolling_multinomial(list(df['Cases']), bias)
        else:
            df['Confirmed'] = df.apply(lambda row: int(row['Cases']
                                       * bias[row['Weekday']]), axis=1)

        df.rename(columns={'Cases': 'Ground Truth'}, inplace=True)
        self.unbiased_report(output_path, df)

    def rolling_multinomial(self, data, bias):
        """For each period of 7 days, redistributes the total number
        of cases according to the bias values
        """
        weights = [i / 7 for i in bias.values()]
        week_count = len(data) // 7
        for w in range(week_count):
            week_data = data[7*w : 7*(w + 1)]
            day_counts = np.random.multinomial(sum(week_data), weights)
            data[7*w : 7*(w + 1)] = day_counts
        return data


