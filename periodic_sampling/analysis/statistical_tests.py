#
# Statistical tests to quantify the extent of periodic variation
#

import numpy as np
import scipy.stats as ss

def single_t_test(data, mu_0 = 1):
    """Testing the null hypothesis that the population mean x_bar
    is equal to a specified value μ0, for a n samples of stamdard
    deviation s.
    
    Test statistic: t = (x_bar-mu_0)/(s/sqrt(n))

    Although the parent population does not need to be normally distributed,
    the distribution of the population of sample means x_bar is assumed
    to be normal.

    By the central limit theorem, if the observations are independent and
    the second moment exists, then t will be approximately normal N(0;1).
    
    Parameters
    ----------
    data : list
        Sample data (n values)
    mu_0 : float
        Comparison (test) populaiton mean
    """
    x_bar = np.mean(data)
    s = np.std(data)
    return (x_bar - mu_0) / (s / np.sqrt(len(data)))

def _p_val(t_stat, dof):
    """Compute p value from t statistic and degrees of freedom
    for a 2-sided t- test.
    
    Parameters
    ----------
    t_stat : float
        The t-statistic from the t test
    dof : int
        The number of degrees of freedom in the test
    """
    return 2*(1 - ss.t.cdf(abs(t_stat), dof))


def weekday_t_tests(df, col, p_vals = True):
    """Conduct a t-test on named column of dataframe for each day of the week
    (dataframe must have 'Day_Index' column to denote this).
    
    Parameters
    ----------
    df : pd.Dataframe
        Dataframe, including col and 'Day_Index
    col : str
        Name of column in dataframe to consider
    p_vals : bool
        Whether to return the p_vals or the t statistic (P_vals by defualt)
    """
    output_stats = []
    for i in range(7):
        output_stats.append(single_t_test(df[df['Day_Index'] == i][col]))
        if p_vals:
            output_stats[i] = _p_val(output_stats[i], len(df[df['Day_Index'] == i][col]) - 1)
    return output_stats


def kruskal_weekday_test(df, col):
    """The Kruskal-Wallis H-test tests the null hypothesis that the population
    median for each weekday are equal for a named column of dataframe provided.
    
    Parameters
    ----------
    df : pd.Dataframe
        Dataframe, including col and 'Day_Index

    Returns
    -------
    float : The Kruskal-Wallis H statistic, corrected for ties.
    float : The p-value for the test using the assumption that 
            H has a chi square distribution.
    """
    weekday_df = []
    for i in range(7):
        weekday_df.append(df[df['Day_Index'] == i][col])
    return ss.kruskal(*weekday_df, nan_policy='omit')
