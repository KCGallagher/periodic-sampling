#
# Collection of functions for our periodic sampling formualtion
# See `fixed_bias_sampler` or `variable_Rt_sampler` for derivations of functions included
#

import numpy as np
import scipy.stats as ss

from sampling_methods import GibbsParameter


#  --- TIMESERIES PARAMETERS ---

def _truth_loglikelihood(params, index, value):
    """The independant probability of a given value for a given index of truth time series.
    
    Parameters
    ----------
    params : Dict
        Dictionary object for all inference variables and associated parameters
    index : int
        Index of timeseries to sample from
    value : int
        Predicted number of events for this element of the timeseries
        
    Returns
    -------
    float : Loglikelihood of the value at the given index in the timeseries
    """
    if ('R_' + str(index)) in params:
        R_value = params['R_' + str(index)]
    else:  # Use constant R value
        R_value = params['R_t']
    
    prob_truth = ss.poisson.logpmf(k=value,
                                mu=_calculate_gamma(params, index) * R_value)

    prob_measurement = ss.poisson.logpmf(k=params['data_' + str(index)],
                                      mu=(params['bias_' + str(index % 7)].value 
                                          * value))
        # Assumes week starts on a monday, otherwise can convert later
    return prob_truth + prob_measurement

def _calculate_gamma(params, max_t):
    """Historic gamma factor for a given index of data series. For more detailed
    description of the gamma factor, see `renewal_model.py`.
    
    Parameters
    ----------
    params : Dict
        Dictionary object for all inference variables and associated parameters
    max_t : int
        Maximum index of timeseries to calculate gamma up to
        
    Returns
    -------
    float : Loglikelihood of the value at the given index in the timeseries
    """
    if max_t == 0:
        return (params['data_0'] / params['bias_0'])  # Best guess of initial point
    omega = params['serial_interval']
    cases = [params[k] for k in params.keys() if k.startswith('data_')]
    n_terms_gamma = min(max_t + 1, len(omega))  # Number of terms in sum for gamma
    if max_t < len(omega):
        omega = omega / sum(omega[:n_terms_gamma])
    return sum([omega[i] * cases[max_t - i] for i in range(1, n_terms_gamma)])

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

def _timeseries_truth_sample(params, index):
    """Independent sample of a single datapoint from the truth timeseries.
    
    Parameters
    ----------
    params : Dict
        Dictionary object for all inference variables and associated parameters
    index : int
        Index of timeseries to sample from
        
    Returns
    -------
    int : Sampled value of given index of timeseries
    """
    weights = []
    values = range(max(1, 2 * params['data_' + str(index)]))
    for val in values:
        # Checks values from 0 to 2 * current value
        # Safeguard that it should check up to 1 at least in case current value is poor
        weights.append(_truth_loglikelihood(params, index, val)) # for value
    
    index = _categorical_log(weights)
    return values[index]

def truth_parameter(value, index):
    """Creates parameter object for a single data point of known index 
    in truth array. 

    Uses Gibbs framework, but samples next values indepedently, rather 
    than from the conditional distribution (the sample method of the
    parameter is overwritten to allow this).

    Parameters
    ----------
    index : int
        Index of timeseries to generate a parameter for
    value : int
        Initial value for this parameter object
        
    Returns
    -------
    GibbsParameter : Parameter object for given index of timeseries
    """
    param = GibbsParameter(value=value, conditional_posterior=None)
    # overwrite sampling method for parameter to use independant sampling
    param.sample = lambda params : _timeseries_truth_sample(params, index=index)
    return param

#  --- BIAS PARAMETERS ---

def _bias_pdf_params(index, **kwargs):
    """Parameters for the probability density function (pdf) for 
    a given index of the bias vector.
    
    Parameters
    ----------
    index : int
        Index of bias vector to generate the pdf for
    kwargs : Unpacked dict
        Unpacked collection of parameters objects
        
    Returns
    -------
    dict : Parameters for the conditional posterior used in sampling
    """
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
    correct index, and can be passed the unpacked params dictionary.
    
    Parameters
    ----------
    index : int
        Index of bias vector to generate the pdf for
    value : int
        Initial value for this parameter object
        
    Returns
    -------
    GibbsParameter : Parameter object for given index of bias vector
    """
    return GibbsParameter(
        value=value, conditional_posterior=ss.gamma.rvs,
        posterior_params = lambda **kwargs : _bias_pdf_params(index=index, value=value, **kwargs))

#  --- R PARAMETERS (constant and variable R)---

def _rt_params(index=None, **kwargs):
    """Parameters for the probability density function (pdf) for 
    a single (constant) reproductive number.
    
    Parameters
    ----------
    index : int
        Index of the timeseries to which this Rt value corresponds. Pass 'None' if
        the R value is constant over time
    kwargs : Unpacked dict
        Unpacked collection of parameters objects
        
    Returns
    -------
    dict : Parameters for the conditional posterior used in sampling
    """
    params = kwargs

    if index is None:  # For constant R case - considers whole timeseries
        window_start = 0
    else:  # To compute params for a single index of a time varying Rt 
        window_start = max(0, index-params['Rt_window'])  # Typically -7 for one week
        index += 1  # So range includes current value

    unsorted_indicies = [int(k[len('data_'):]) for k in params.keys() if k.startswith('data_')]
    data_indicies = [k for k in sorted(unsorted_indicies)]
    data_values = []; gamma_values = []

    for i in data_indicies[window_start:index]:
        data_values.append(params['data_' + str(i)])
        gamma_values.append(_calculate_gamma(params, i))

    gamma_params = {'a': params['rt_prior_alpha'] + sum(data_values),
                   'scale': 1 / (params['rt_prior_beta'] + sum(gamma_values))
                   }  # scale is inverse of beta value
    
    return gamma_params

def fixed_r_parameter(value):
    """Parameters for the probability density function (pdf) for 
    a single (constant) reproductive number.
    
    Parameters
    ----------
    value : int
        Initial value for this parameter object
    
    Returns
    -------
    GibbsParameter : Parameter object for constant reproductive number    
        """
    return GibbsParameter(value=value, conditional_posterior=ss.gamma.rvs, 
                            posterior_params=lambda **kwargs : _rt_params(index=None, **kwargs))

def rt_parameter(value, index):
    """Parameters for the probability density function (pdf) for 
    a single (constant) reproductive number.
    
    Parameters
    ----------
    value : int
        Initial value for this parameter object
    index : int
        Index of the timeseries to which this Rt value corresponds
    
    Returns
    -------
    GibbsParameter : Parameter object for constant reproductive number    
        """
    return GibbsParameter(value=value, conditional_posterior=ss.gamma.rvs, 
                            posterior_params=lambda **kwargs : _rt_params(index=index, **kwargs))