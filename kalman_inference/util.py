import numpy as np
import scipy.stats
import pandas as pd
import copy

def poisson_rvs(mu):
    return scipy.stats.poisson.rvs(mu)


def negativebinomial_rvs(mu, kappa, n=1):
    n1 = kappa
    p = float(kappa) / (kappa + mu)
    return scipy.stats.nbinom.rvs(n1, p, 0, n)


def expected_cases(Rt, past_cases, serial_interval):
    if np.abs(sum(serial_interval) - 1) > 1e-6:
        raise ValueError("Serial interval does not sum to 1.")
    return Rt * np.dot(past_cases, serial_interval)


def next_cases(Rt, past_cases, serial_interval, kappa):
    expectation = expected_cases(Rt, past_cases, serial_interval)
    if kappa is not None:
        return negativebinomial_rvs(expectation, kappa)
    else:
        return poisson_rvs(expectation)


def generate_case_series(Rt_series, past_cases, serial_interval, kappa=None, obs_func=None):
    n_past_cases = len(past_cases)
    if n_past_cases != len(serial_interval):
        raise ValueError("Past cases must be of same length as serial interval.")
    series_len = len(Rt_series)
    cases = np.zeros(series_len + n_past_cases)
    cases[:n_past_cases] = past_cases
    for i in range(series_len):
        new_case_index = i + n_past_cases
        historical_cases = cases[i:new_case_index]
        historical_cases_rev = historical_cases[::-1]
        cases[new_case_index] = next_cases(
            Rt_series[i], historical_cases_rev, serial_interval, kappa)
    cases_post_past = cases[n_past_cases:]
    days = np.arange(1, len(cases_post_past) + 1)

    if obs_func is not None:
        obs_cases = []
        for t in range(len(cases_post_past)):
            obs_cases.append(obs_func(cases_post_past[:t+1]))
    else:
        obs_cases = copy.copy(cases_post_past)

    df = pd.DataFrame(
        {'day': days,
        'cases': cases_post_past,
        'obs_cases': obs_cases,
        'Rt': Rt_series})
    return df
