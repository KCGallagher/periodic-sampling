import datetime
import stan
import numpy as np
import pandas as pd
import scipy.stats as ss
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = '14'

from periodic_sampling.synthetic_data import RenewalModel, Reporter

# Simulate Renewal Model
time_steps = 100; N_0 = 100; seed=41; R0 = 0.99
start_date = '01/01/2020'; bias_method = 'scale'

bias = [0.5, 1.4, 1.2, 1.1, 1.1, 1.1, 0.6]  # Always given with monday first

np.random.seed(seed)
model = RenewalModel()
model.simulate(T=time_steps, N_0=N_0, R_0=0.99)

# Report unbiased and biased data
rep = Reporter(model.case_data, start_date=start_date)  # Start on Mon 6th for ease

truth_df = rep.unbiased_report()
bias_df = rep.fixed_bias_report(bias=bias, method=bias_method)

with open("stan_inference/fixed_bias_example.stan") as f:
    fixed_bias_code = f.read()

fixed_bias_data = {
    "C": list(bias_df['Confirmed']),
    "R": 0.99,
    "serial_interval": RenewalModel(R0=None).serial_interval
}

posterior = stan.build(fixed_bias_code, data=fixed_bias_data, random_seed=1) 
fit = posterior.sample(num_chains=4, num_samples=10)
df = fit.to_frame()
print(df.describe().T)

