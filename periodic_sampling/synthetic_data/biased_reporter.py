#
# Class to report case data with periodic biases
#

import math
import numpy as np
import scipy.stats as ss
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
        
        Parameters
        ----------
        output_path : str
            Path to output csv with reported data. If none,
            returns the output dataframe.
        df : pd.Dataframe
            Input dataframe to report on - used for internal specification.
            By default uses self.case_data (recommended for external use).
        """
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
            Path to output csv with reported data. If none,
            returns the output dataframe.
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
            df['Confirmed'] = self._rolling_multinomial(df, bias)
        else:
            df['Confirmed'] = df.apply(lambda row: int(row['Cases']
                                       * bias[row['Weekday']]), axis=1)

        df.rename(columns={'Cases': 'Ground Truth'}, inplace=True)
        self.unbiased_report(output_path, df)

        if output_path is None:
            return df

    def _rolling_multinomial(self, df, bias):
        """For each period of 7 days, redistributes the total number
        of cases according to the bias values
        """
        data = list(df['Cases'].copy())
        weights = [i / 7 for i in bias.values()]
        week_count = len(data) // 7

        first_day_index = df['Date'][0].weekday()
        weights = [weights[(i+first_day_index) % 7] for i in range(7)]

        for w in range(week_count):
            week_data = data[7*w : 7*(w + 1)]
            day_counts = np.random.multinomial(sum(week_data), weights)
            data[7*w : 7*(w + 1)] = day_counts
        return data

    def delay_distribution_report(self, params, output_path=None):
        """Assumes a separate delay distribution for each
        day of the week. The distribution is a discretised
        gamma, characterised by the mean and std, and capped at
        6 days (i.e. no case/death reporting delay can be longer
        than 6 days).
        
        Parameters
        ----------
        params : Dict
            Dictionary of lists - each list is the set of
            weekday values for a named distribution parameter.
        output_path : str
            Path to output csv with reported data. If none, 
            return the output dataframe.
        """

        df = self.case_data.copy()
        case_data = list(df['Cases'])

        for i, value in enumerate(list(df['Cases'].copy())):
            day_index = df['Date'][i].weekday()
            delay_values = self._discrete_gamma_delay(value, params['shape'][day_index],
                                                     params['rate'][day_index])

            # Update case-data with new counts
            case_data[i] -= sum(delay_values)
            for j, d_value in enumerate(delay_values):
                try:
                    case_data[i + j] += d_value
                except IndexError:  # Occurs at end of dataset
                    continue
 
        df['Confirmed'] = case_data
        df.rename(columns={'Cases': 'Ground Truth'}, inplace=True)
        self.unbiased_report(output_path, df)

        if output_path is None:
            return df

    def _discrete_gamma_delay(self, value, shape, rate):
        """Takes a value of cases on a given day, and returns the 
        reported number of cases on each day in the next week (including
        the original day) based on a discrete gamma distribution, 
        with stochastic rounding."""
        unnorm_dist = ss.gamma.pdf(x=list(range(7)), a=shape, scale=1/rate)
        data_bias = (unnorm_dist / (sum(unnorm_dist))) * value
        return [math.floor(x + np.random.uniform()) for x in data_bias]

