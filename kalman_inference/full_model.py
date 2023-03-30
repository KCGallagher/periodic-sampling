import stan
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import math
from util import *

plt.rcParams['font.size'] = '14'

dist1 = [0.2, 0.5, 0.3]
dist2 = [0.85, 0.15, 0.0]

weekly_delay = [dist1] * 2 + [dist2] * 5

sigma = 0.1


def obs_process_delay(I):
    day = len(I)
    obs_operator = [weekly_delay[(day - s) % 7][s] for s in range(3)]
    hist_cases = I[-3:]
    mean = np.asarray(obs_operator)[::-1][:len(hist_cases)] @ hist_cases
    return random.gauss(mean, sigma*math.sqrt(mean))


serial_interval = pd.read_csv("kalman_inference/covid_serial_interval.csv")
w = serial_interval['w']
wmax = 20
w = w[:wmax]
w = w / sum(w)


np.random.seed(111)
past_cases = np.zeros(len(w))
past_cases[-1] = 100
past_cases[-2] = 100
past_cases[-3] = 100

Rt_part_1 = np.repeat(1.3, 50)
Rt_part_2 = np.repeat(0.8, 50)

Rt_series = np.concatenate([Rt_part_1, Rt_part_2])

cases_df = generate_case_series(
    Rt_series,
    past_cases,
    w,
    obs_func=obs_process_delay)

cases = cases_df['cases']
obs_cases = cases_df['obs_cases']


with open("kalman_inference/kalman_filter_delay.stan") as f:
    stan_code = f.read()

stan_data = \
    {
        'N': len(cases),
        'K': 2,
        'window': [1] * 50 + [2] * 50,
        'C': np.asarray(cases),
        'wmax': wmax,
        'w': np.asarray(w),
        'I_history': np.asarray(past_cases)[::-1]
    }


posterior = stan.build(stan_code, data=stan_data, random_seed=1)

fit = posterior.sample(num_chains=4, num_samples=10)

df = fit.to_frame()
print(df.describe().T)
