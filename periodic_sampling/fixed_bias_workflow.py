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

####### INFERENCE METHODS #######

@profile
def truth_loglikelihood(params, index, value):
    """The independant probability of a given value for a given index of truth time series."""
    prob_truth = ss.poisson.logpmf(k=value,
                                mu=_calculate_gamma(params, index) * params['R_t'])

    prob_measurement = ss.poisson.logpmf(k=params['data_' + str(index)],
                                      mu=(params['bias_' + str(index % 7)].value 
                                          * value))
        # Assumes week starts on a monday, otherwise can convert later
    # if index == 0:
    #     print([value, prob_truth, prob_measurement])
    return prob_truth + prob_measurement

@profile
def _calculate_gamma(params, max_t):
    """Historic gama factor for a given index of data series"""
    if max_t == 0:
        return (params['data_0'] / params['bias_0'].value)  # Best guess of initial point
    omega = params['serial_interval']
    cases = [params[k] for k in params.keys() if k.startswith('data_')]
    n_terms_gamma = min(max_t + 1, len(omega))  # Number of terms in sum for gamma
    if max_t < len(omega):
        omega = omega / sum(omega[:n_terms_gamma])
    return sum([omega[i] * cases[max_t - i] for i in range(1, n_terms_gamma)])

@profile
def _categorical_log(log_p):
    """Generate one sample from a categorical distribution with event
    probabilities provided in log-space. Credit to Richard Creswell.

    Parameters
    ----------
    log_p : array_like
        logarithms of event probabilities, which need not be normalized

    Returns
    -------
    int
        One sample from the categorical distribution, given as the index of that
        event from log_p.
    """
    exp_sample = np.log(np.random.random())
    events = np.logaddexp.accumulate(np.hstack([[-np.inf], log_p]))
    events -= events[-1]
    sample = next(x[0]-1 for x in enumerate(events) if x[1] >= exp_sample)
    return sample

@profile
def truth_sample(params, index):
    """Independent sample of a single datapoint from the truth timeseries."""
    weights = []
    values = range(max(150, 2 * params['data_' + str(index)]))
    for val in values:
        # Checks values from 0 to 2 * current value
        # Safeguard that it should check up to 150 at least in case current value is poor
        weights.append(truth_loglikelihood(params, index, val)) # for value
    
    index = _categorical_log(weights)
    return values[index]

@profile
def bias_pdf_params(index, value, **kwargs):
    """Parameters for the probability density function (pdf) for 
    a given index of the bias vector."""
    # params = locals()  # Collect kwargs back into one params dictionary
    params = kwargs

    unsorted_indicies = [int(k[len('data_'):]) for k in params.keys() if k.startswith('data_')]
    data_indicies = [k for k in sorted(unsorted_indicies)]
    data_values = []; truth_values = []

    for i in data_indicies:
        if int(i) % 7 == index:
            data_values.append(params['data_' + str(i)])
            truth_values.append(params['truth_' + str(i)])

    gamma_params = {'a': params['bias_prior_alpha'] + sum(data_values),
                   'scale': 1 / (params['bias_prior_beta'] + sum(truth_values))
                   }  # scale is inverse of beta value
    
    return gamma_params

def bias_parameter(value, index):
    """Creates Gibbs parameter object, with a gamma posterior derived
    using conjugate priors above. Function object is created for the
    correct index, and can be passed the unpacked params dictionary."""
    return GibbsParameter(
        value=value, conditional_posterior=ss.gamma.rvs,
        posterior_params = lambda **kwargs : bias_pdf_params(index=index, value=value, **kwargs))

def truth_parameter(value, index):
    """Creates parameter object for a single data point of known index 
    in truth array. 

    Uses Gibbs framework, but samples next values indepedently, rather 
    than from the conditional distribution (the sample method of the
    parameter is overwritten to allow this).
    """
    param = GibbsParameter(value=value, conditional_posterior=None)
    # overwrite sampling method for parameter to use independant sampling
    param.sample = lambda params : truth_sample(params, index=index)
    return param

####### INFERENCE WORKFLOW #######

# Simulate Renewal Model
time_steps = 30; N_0 = 100; R_0=0.99; seed=42
start_date = '01/01/2020'
bias = [0.5, 1.4, 1.2, 1.1, 1.1, 1.1, 0.6]  # Always given with monday first

np.random.seed(seed)
model = RenewalModel(R0=R_0)
model.simulate(T=time_steps, N_0=N_0)

# Report unbiased and biased data
rep = Reporter(model.case_data, start_date=start_date)  # Start on Mon 6th for ease

truth_df = rep.unbiased_report()
bias_df = rep.fixed_bias_report(bias=bias, method='multinomial')

I_data = list(bias_df['Confirmed'])
params = {'bias_prior_alpha': 1, 'bias_prior_beta': 1}  # Gamma dist

params['R_t'] = R_0  # Start with known R_t (0.99)
params['serial_interval'] = RenewalModel(R0=params['R_t']).serial_interval

for i, val in enumerate(I_data):  # Observed cases - not a Parameter
    params[("data_" + str(i))] = val

data_initial_guess = sum(I_data)/len(I_data)  # Constant initial value
for i in range(0, len(I_data)):  # Ground truth data
    params[("truth_" + str(i))] = truth_parameter(data_initial_guess, index=i)

for i in range(7):  # Weekday bias parameters
    params[("bias_" + str(i))] = bias_parameter(1, index=i)

step_num = 2
sampler = MixedSampler(params=params)
output = sampler.sampling_routine(step_num=step_num, sample_burnin=1)

filename = f"synth_inference_T_{time_steps}_N0_{N_0}_R0_{R_0}_It_{step_num}_seed_{seed}.csv"
output.to_csv('data/outputs/' + filename)

start_index = datetime.datetime.strptime(start_date, "%d/%m/%Y").weekday()
output_bias = [np.round(np.mean(output['bias_' + str((i - start_index) % 7)]), 1) for i in range(7)]

print("Mean bias values: " + str(output_bias))
print(f"True bias values: {bias}")

