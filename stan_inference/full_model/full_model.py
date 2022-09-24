import stan
import numpy as np
import pandas as pd

from periodic_sampling.synthetic_data import RenewalModel, Reporter

# Used for smoothing stepped R profile

def smoothen_Rt(my_list, window):
    f_padding = [my_list[0]] * window
    smooth_list = list(pd.Series(f_padding + my_list).rolling(window=window, min_periods=1, center=True).mean())
    return smooth_list[window:]

# Simulate Renewal Model
time_steps = 600; N_0 = 1000; seed=41; R0_diff = 0.1; R_n = 10
start_date = '01/01/2020'; bias_method = 'poisson'

bias = [0.5, 1.4, 1.2, 1.1, 1.1, 1.1, 0.6]  # Always given with monday first

R0_list = [1.0 - R0_diff * (2 * (i // (time_steps/R_n) % 2) - 1) for i in range(time_steps)]
R0_list = smoothen_Rt(R0_list, window=40)

np.random.seed(seed); model = RenewalModel()
model.simulate(T=time_steps, N_0=N_0, R_0=R0_list);

# Report unbiased and biased data
rep = Reporter(model.case_data, start_date=start_date) 

truth_df = rep.unbiased_report()
bias_df = rep.fixed_bias_report(bias=bias, method=bias_method)

with open("stan_inference/full_model/full_model.stan") as f:
    fixed_bias_code = f.read()

c_val = list(bias_df['Confirmed'])

fixed_bias_data = {
    "time_steps": len(c_val),
    "C": c_val,
    "Rt_window": 2,
    "serial_interval": RenewalModel(R0=None).serial_interval,
    "alpha_prior": [1 for _ in range(7)]  # larger val -> tighter dist
}

posterior = stan.build(fixed_bias_code, data=fixed_bias_data, random_seed=1) 

chain_num = 4
sample_num = int(2e4)
bias_init_val = [1/7 for _ in range(7)]  # ((i+1)/28) for simplex step
rt_init_val = [1 for _ in range(fixed_bias_data['time_steps'])]
init_values = [{'alpha': bias_init_val, 'R': rt_init_val} for _ in range(chain_num)] 

fit = posterior.sample(num_chains=chain_num, num_samples=sample_num, 
                       num_thin=int(2e1),
                       init=init_values,
                       )
df = fit.to_frame()
df = df[df.columns.drop([c for c in df.columns if c.startswith('alpha')])]
print(df.describe().T)

filename = f"stan_inference_T_{bias_method}_{time_steps}_N0_{N_0}_R_n_{R_n}_R0diff_{R0_diff}_It_{sample_num}_seed_{seed}.csv"
df.to_csv("stan_inference/full_model/" + filename)
