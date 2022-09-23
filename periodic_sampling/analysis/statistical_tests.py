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
        Whether to return the p_vals or the t statistic (True by defualt)
    """
    output_stats = []
    for i in range(7):
        output_stats.append(single_t_test(df[df['Day_Index'] == i][col]))
        if p_vals:
            output_stats[i] = _p_val(output_stats[i], len(df[df['Day_Index'] == i][col]) - 1)
    return output_stats


def wilcoxon_signed_rank_test(df, col_1, col_2, p_vals = True):
    """The Wilcoxon signed-rank test tests the null hypothesis that two related 
    paired samples come from the same distribution. In particular, it tests 
    whether the distribution of the differences x - y is symmetric about zero. 
    It is a non-parametric version of the paired T-test.
    
    Parameters
    ----------
    df : pd.Dataframe
        Dataframe, including col and 'Day_Index
    col : str
        Name of column in dataframe to consider
    p_vals : bool
        Whether to return the p_vals or the t statistic (True by defualt)
    """
    output_stats = []
    for i in range(7):
        output_stats.append(ss.wilcoxon(df[df['Day_Index'] == i][col_1],
                                        df[df['Day_Index'] == i][col_2],
                                        nan_policy='omit'))
        if p_vals:
            output_stats[i] = output_stats[i].pvalue
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


def multiple_comparisons_correction(p_vals, alpha=0.05):
    """Uses the Benjamini-Hochberg procedure to combine the p values from
    multiple independent null hypothesis test results.
    
    Parameters
    ----------
    p_vals : list
        List of independent p values
    alpha : float
        Significance level (the probability of rejecting the 
        null hypothesis when it is true)

    Output
    ------
    list[bool] : Whether to accept H0 for each hypothesis (ordered)
    """
    sorted_vals = sorted(p_vals)
    k = 0  # Number of null hypotheses to reject
    for i in range(len(p_vals)):
        if sorted_vals[i] <= ((i + 1) * alpha / len(p_vals)):
            k = (i + 1)
    
    passed_H0 = [True for _ in range(len(p_vals))]
    for n in range(k):
        failed_test_index = p_vals.index(sorted_vals[n])
        passed_H0[failed_test_index] = False
        p_vals[failed_test_index] = None  # Prevent refinding this value in case of duplicates

    return passed_H0
