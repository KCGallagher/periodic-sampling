#
# Replica of the sampler script, used for code profiling
# To profile, decorate desired functions with @profile (will look at top level only)
# Run `python3 kernprof.py -l periodic_sampling/fixed_bias_workflow.py`` to profile
# Run `python3 -m line_profiler fixed_bias_workflow.py.lprof' to view results
#
# Current results indicate sampling the logpdf from the possion dist for the data point
# independent sampling is heaviest - this could be reduced by targeted sampling (i.e. 
# coarse sampling across whole range, then finer sampling in most likely region),
# however this cost is fundamentally not easily avoided (and outweighs any potential
# benefits of optimisation elsewhere in the code.)
#

import datetime
import numpy as np
import pandas as pd
import scipy.stats as ss
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = '12'

from synthetic_data import RenewalModel, Reporter
from sampling_methods import GibbsParameter, MixedSampler
from periodic_model import truth_parameter, bias_parameter, rt_parameter



####### INFERENCE WORKFLOW #######

# # Simulate Renewal Model
# time_steps = 30; N_0 = 100; R_0=0.99; seed=42
# start_date = '01/01/2020'
# bias = [0.5, 1.4, 1.2, 1.1, 1.1, 1.1, 0.6]  # Always given with monday first

# np.random.seed(seed)
# model = RenewalModel(R0=R_0)
# model.simulate(T=time_steps, N_0=N_0)

# # Report unbiased and biased data
# rep = Reporter(model.case_data, start_date=start_date)  # Start on Mon 6th for ease

# truth_df = rep.unbiased_report()
# bias_df = rep.fixed_bias_report(bias=bias, method='multinomial')

# I_data = list(bias_df['Confirmed'])
# params = {'bias_prior_alpha': 1, 'bias_prior_beta': 1}  # Gamma dist

# params['R_t'] = R_0  # Start with known R_t (0.99)
# params['serial_interval'] = RenewalModel(R0=params['R_t']).serial_interval

# for i, val in enumerate(I_data):  # Observed cases - not a Parameter
#     params[("data_" + str(i))] = val

# data_initial_guess = sum(I_data)/len(I_data)  # Constant initial value
# for i in range(0, len(I_data)):  # Ground truth data
#     params[("truth_" + str(i))] = truth_parameter(data_initial_guess, index=i)

# for i in range(7):  # Weekday bias parameters
#     params[("bias_" + str(i))] = bias_parameter(1, index=i)

# step_num = 2
# sampler = MixedSampler(params=params)
# output = sampler.sampling_routine(step_num=step_num, sample_burnin=1)

# filename = f"synth_inference_T_{time_steps}_N0_{N_0}_R0_{R_0}_It_{step_num}_seed_{seed}.csv"
# output.to_csv('data/outputs/' + filename)

# start_index = datetime.datetime.strptime(start_date, "%d/%m/%Y").weekday()
# output_bias = [np.round(np.mean(output['bias_' + str((i - start_index) % 7)]), 1) for i in range(7)]

# print("Mean bias values: " + str(output_bias))
# print(f"True bias values: {bias}")


####### MULTI-TIMESERIES WORKFLOW

# # Simulate Renewal Model
# time_steps = 600; N_0 = 100; R_0=0.99; 
# start_date = '01/01/2020'; bias_method = 'poisson'
# bias = [0.5, 1.4, 1.2, 1.1, 1.1, 1.1, 0.6]  # Always given with monday first

# step_num = 100; seeds = list(range(20))

# output = pd.DataFrame()
# for seed in seeds:
#     print("Interation: " + str(seed))
#     np.random.seed(seed)
#     model = RenewalModel(R0=R_0)
#     model.simulate(T=time_steps, N_0=N_0, display_progress=False)

#     rep = Reporter(model.case_data, start_date=start_date)  # Start on Mon 6th for ease
#     bias_df = rep.fixed_bias_report(bias=bias, method=bias_method)

#     I_data = list(bias_df['Confirmed'])
#     params = {'bias_prior_alpha': 1, 'bias_prior_beta': 1}  # Gamma dist

#     params['R_t'] = R_0  # Start with known R_t (0.99)
#     params['serial_interval'] = RenewalModel(R0=params['R_t']).serial_interval

#     for i, val in enumerate(I_data):  # Observed cases - not a Parameter
#         params[("data_" + str(i))] = val

#     data_initial_guess = sum(I_data)/len(I_data)  # Constant initial value
#     for i in range(0, len(I_data)):  # Ground truth data
#         params[("truth_" + str(i))] = truth_parameter(data_initial_guess, index=i)

#     for i in range(7):  # Weekday bias parameters
#         params[("bias_" + str(i))] = bias_parameter(1, index=i)

#     sampler = MixedSampler(params=params)
#     output = pd.concat([output, sampler.sampling_routine(step_num=step_num, sample_burnin=1)], axis=0)

# filename = f"synth_inference_T_{time_steps}_N0_{N_0}_R0_{R_0}_It_{step_num}_seeds_{len(seeds)}.csv"
# output.to_csv('data/outputs/multiseries/' + filename)

# start_index = datetime.datetime.strptime(start_date, "%d/%m/%Y").weekday()
# output_bias = [np.round(np.mean(output['bias_' + str((i - start_index) % 7)]), 1) for i in range(7)]

# histos = output.hist([("bias_" + str((i - start_index) % 7)) for i in range(7)], bins=20, figsize=(15, 4), layout=(2, 4));
# weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# for i in range(7):
#     histos.flatten()[i].set_tiseed=41;
# print("Mean bias values: " + str(output_bias))
# print(f"True bias values: {bias}")

# for i in range(7):
#     mean = np.round(np.mean(output['bias_' + str((i - start_index) % 7)]), 2)
#     std = np.round(np.std(output['bias_' + str((i - start_index) % 7)]), 2)
#     print(f"Bias_{i}: {mean} +/- {std}")


####### VARIABLE RT, MULTI-CHAIN WORKFLOW

# Simulate Renewal Model
time_steps = 100; N_0 = 100; R0_diff = 0.2
start_date = '01/01/2020'; bias_method = 'scale'
bias = [0.5, 1.4, 1.2, 1.1, 1.1, 1.1, 0.6]  # Always given with monday first
R0_list = ([1.0 + R0_diff] * int(time_steps/2)) + ([1.0 - R0_diff] * int(time_steps/2))

seeds = list(range(6)); output = pd.DataFrame()
step_num = 500
output1 = pd.DataFrame()

# for seed in seeds:
#     np.random.seed(41)
#     model = RenewalModel()
#     model.simulate(T=time_steps, N_0=N_0, R_0=R0_list)

#     # Report unbiased and biased data
#     rep = Reporter(model.case_data, start_date=start_date)  
#     truth_df = rep.unbiased_report()
#     bias_df = rep.fixed_bias_report(bias=bias, method=bias_method)

#     np.random.seed(seed)
#     I_data = list(bias_df['Confirmed'])

#     params = {'bias_prior_alpha': 1, 'bias_prior_beta': 1,
#             'rt_prior_alpha': 1, 'rt_prior_beta': 1}  # Gamma dist

#     params['serial_interval'] = RenewalModel(R0=None).serial_interval
#     params['Rt_window'] = 7  # Assume it is constant for 7 days

#     for i, val in enumerate(I_data):  # Observed cases - not a Parameter
#         params[("data_" + str(i))] = val

#     data_initial_guess = sum(I_data)/len(I_data)  # Constant initial value
#     for i in range(0, len(I_data)):  # Ground truth data
#         params[("truth_" + str(i))] = truth_parameter(data_initial_guess, index=i)

#     for i in range(7):  # Weekday bias parameters
#         params[("bias_" + str(i))] = bias_parameter(value=2 * np.random.random(), index=i)

#     params["R_t"] = 1


#     sampler = MixedSampler(params=params)
#     output1 = pd.concat([output1, sampler.sampling_routine(step_num=step_num,
#                                                          sample_burnin=0,
#                                                          chain_num=seed)],
#                          axis=0)
    

# filename = f"step1_inference_T_{bias_method}_{time_steps}_N0_{N_0}_R0diff_{R0_diff}_It_{step_num}_seeds_{seed+1}.csv"
# output1.to_csv('data/outputs/stepped_R/multichain/fixed_r_stage/' + filename)

output1 = pd.read_csv('data/outputs/stepped_R/multichain/fixed_r_stage/step1_fixed_inference_T_scale_100_N0_100_R0diff_0.2_It_500_seeds_6.csv')

np.random.seed(41)
model = RenewalModel()
model.simulate(T=time_steps, N_0=N_0, R_0=R0_list)
rep = Reporter(model.case_data, start_date=start_date) 

bias_df = rep.fixed_bias_report(bias=bias, method=bias_method)
I_data = list(bias_df['Confirmed'])

seeds = list(range(4)); 
step_num = int(300)
output2 = pd.DataFrame()

input = output1.mean()
for seed_i, seed in enumerate(seeds):
    np.random.seed(seed+10)

    params = {'bias_prior_alpha': 1, 'bias_prior_beta': 1,
            'rt_prior_alpha': 1, 'rt_prior_beta': 1}  # Gamma dist

    params['serial_interval'] = RenewalModel(R0=None).serial_interval
    params['Rt_window'] = 1  # Assume it is constant for 7 days

    for i, val in enumerate(I_data):  # Observed cases - not a Parameter
        params[("data_" + str(i))] = val

    data_initial_guess = sum(I_data)/len(I_data)  # Constant initial value
    for i in range(0, len(I_data)):  # Ground truth data
        params[("truth_" + str(i))] = input[("truth_" + str(i))] 

    for i in range(7):  # Weekday bias parameters
        params[("bias_" + str(i))] = input[("bias_" + str(i))]

    for i in range(0, len(I_data)):  # Reproductive number values
        params[("R_" + str(i))] = rt_parameter(value=3, index=i)


    sampler = MixedSampler(params=params)
    output2 = pd.concat([output2, sampler.sampling_routine(step_num=step_num,
                                                         sample_burnin=0,
                                                         chain_num=seed)],
                         axis=0)
    

filename = f"step2_fixed_inference_T_{bias_method}_{time_steps}_N0_{N_0}_R0diff_{R0_diff}_It_{step_num}_seeds_{seed+1}.csv"
output2.to_csv('data/outputs/stepped_R/multichain/fixed_r_stage/' + filename)