import stan
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = '14'

from periodic_sampling.synthetic_data import RenewalModel, Reporter

# Simulate Renewal Model
time_steps = 100; N_0 = 100; seed=41; R0 = 0.99
start_date = '07/01/2020'; bias_method = 'scale'

bias = [0.5, 1.4, 1.2, 1.1, 1.1, 1.1, 0.6]  # Always given with monday first

np.random.seed(seed)
model = RenewalModel()
model.simulate(T=time_steps, N_0=N_0, R_0=0.99)

# Report unbiased and biased data
rep = Reporter(model.case_data, start_date=start_date)  # Start on Mon 6th for ease

truth_df = rep.unbiased_report()
bias_df = rep.fixed_bias_report(bias=bias, method=bias_method)

with open("stan_inference/fixed_bias/fixed_dirichlet_bias.stan") as f:
    fixed_bias_code = f.read()

c_val = list(bias_df['Confirmed'])

fixed_bias_data = {
    "time_steps": len(c_val),
    "C": c_val,
    "R": 0.99,
    "serial_interval": RenewalModel(R0=None).serial_interval,
    "alpha_prior": [1 for _ in range(7)]  # larger val -> tighter dist
}

posterior = stan.build(fixed_bias_code, data=fixed_bias_data, random_seed=1) 

bias_init_val = [1/7 for _ in range(7)]  # ((i+1)/28) for simplex step
chain_num = 4
init_values = [{'alpha': bias_init_val} for _ in range(chain_num)]  # List of dict for each chain

fit = posterior.sample(num_chains=chain_num, num_samples=int(1e5), 
                       num_thin=int(1e3),
                    #    num_warmup=20,
                       init=init_values,
                       )
df = fit.to_frame()
df = df[df.columns.drop([c for c in df.columns if c.startswith('alpha')])]
print(df.describe().T)

# Increasing dirichlet prior to 1e6 does decrease sample variance, but no change for sensible values
# No observable change from bias_init_values
