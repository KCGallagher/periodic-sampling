#
# Collection of functions for our periodic sampling formualtion
# See `fixed_bias_sampler` or `variable_Rt_sampler` for derivations of functions included
#

from ast import Lambda
import math
import numpy as np
import scipy.stats as ss

from sampling_methods import GibbsParameter


#  --- TIMESERIES PARAMETERS ---

def _ramanujan_approx(n):
    """Approximation to log(n!) for large n to avoid integer overflow"""
    if n==0:
        return 0
    return n*math.log(n) - n + math.log(n*(1+4*n*(1+2*n)))/6 + math.log(math.pi)/2

def _poisson_logpmf(k, mu):
    """Intended to replace `ss.poisson.logpmf`, giving a x4 speed increase.
    Uses log(x**k) = k/log_x(e) and Ramanujan approximation for log(k!) to
    handle large values of k.
    
    Parameters
    ----------
    k : float
        Predicted number of events
    mu : float 
        Average number of events (mean of Poisson distribution)
        
    Returns
    -------
    float : Log of the pmf function
    """
    if mu == 0:
        return -1e10  # Should be -inf but throws issues in sampling
    if mu == 1:
        return -mu
    return (-mu + (k/math.log(math.e, mu)) - _ramanujan_approx(k))

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
    else:  # Find most recent R value
        times = [name[2:] for name in params.keys() if name.startswith('R_')]
        R_value = params['R_' + str(max(times))]

    prob_truth = _poisson_logpmf(k=value,
                                    mu=_calculate_lambda(params, index) * R_value)

    prob_measurement = _poisson_logpmf(k=params['data_' + str(index)],
                                        mu=(params['bias_' + str(index % 7)].value 
                                            * value))        
    return prob_truth + prob_measurement

def _calculate_lambda(params, max_t):
    """Historic lambda factor for a given index of data series. For more detailed
    description of the lambda factor, see `renewal_model.py`.
    
    Parameters
    ----------
    params : Dict
        Dictionary object for all inference variables and associated parameters
    max_t : int
        Maximum index of timeseries to calculate lambda up to
        
    Returns
    -------
    float : Loglikelihood of the value at the given index in the timeseries
    """
    if max_t == 0:
        return (params['data_0'] / params['bias_0'])  # Best guess of initial point
    omega = params['serial_interval']
    cases = [params[k] for k in params.keys() if k.startswith('data_')]
    n_terms_lambda = min(max_t + 1, len(omega))  # Number of terms in sum for lambda
    if max_t < len(omega):
        omega = omega / sum(omega[:n_terms_lambda])
    return sum([omega[i] * cases[max_t - i] for i in range(1, n_terms_lambda)])

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

def truth_parameter(value, index, sampling_freq = 1):
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
    sampling_freq : int
        Will sample this parameter 1 in every 'sampling_freq' iterations - 
        defaults to unity (i.e. sampling every iteration)
        
    Returns
    -------
    GibbsParameter : Parameter object for given index of timeseries
    """
    param = GibbsParameter(value=value, conditional_posterior=None, sampling_freq=sampling_freq)
    # overwrite sampling method for parameter to use independant sampling
    param.sample = lambda params : _timeseries_truth_sample(params, index=index)
    return param

#  --- POISSON BIAS PARAMETERS ---

def _poisson_bias_pdf_params(index, **kwargs):
    """Parameters for the probability density function (pdf) for 
    a given index of the bias vector, based on a poisson noise model
    (C_t = Po(alpha_t * I_t)).
    
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

def poisson_bias_parameter(value, index, sampling_freq = 1):
    """Creates Gibbs parameter object, with a gamma posterior derived
    using conjugate priors above. Function object is created for the
    correct index, and can be passed the unpacked params dictionary.
    
    Parameters
    ----------
    index : int
        Index of bias vector to generate the pdf for
    value : int
        Initial value for this parameter object
    sampling_freq : int
        Will sample this parameter 1 in every 'sampling_freq' iterations - 
        defaults to unity (i.e. sampling every iteration)
        
    Returns
    -------
    GibbsParameter : Parameter object for given index of bias vector
    """
    return GibbsParameter(
        value=value, conditional_posterior=ss.gamma.rvs, sampling_freq=sampling_freq,
        posterior_params = lambda **kwargs : _poisson_bias_pdf_params(index=index, value=value, **kwargs))

#  --- SCALE BIAS PARAMETERS ---

def _scale_bias_pdf_params(index, **kwargs):
    """Parameters for the probability density function (pdf) for 
    a given index of the bias vector, based on a scale noise model
    (deterministic scaling of cases with C_t = alpha_t * I_t)
    
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
    R_Lambda_values = []; data_values = []

    for i in data_indicies:
        if int(i) % 7 == index:
            data_values.append(params['data_' + str(i)])
            Lambda_val = _calculate_lambda(params, max_t=i)
            R_Lambda_values.append(params['R_' + str(i)] * Lambda_val)


    gamma_params = {'a': params['bias_prior_alpha'] + sum(data_values),
                   'scale': 1 / (params['bias_prior_beta'] + sum(R_Lambda_values))
                   }  # scale is inverse of beta value
    
    return gamma_params

def scale_bias_parameter(value, index, sampling_freq = 1):
    """Creates Gibbs parameter object, with a gamma posterior derived
    using conjugate priors above. Function object is created for the
    correct index, and can be passed the unpacked params dictionary.

    Should only be used with a variable Rt setup.
    
    Parameters
    ----------
    index : int
        Index of bias vector to generate the pdf for
    value : int
        Initial value for this parameter object
    sampling_freq : int
        Will sample this parameter 1 in every 'sampling_freq' iterations - 
        defaults to unity (i.e. sampling every iteration)
        
    Returns
    -------
    GibbsParameter : Parameter object for given index of bias vector
    """
    return GibbsParameter(
        value=value, conditional_posterior=ss.gamma.rvs, sampling_freq=sampling_freq,
        posterior_params = lambda **kwargs : _scale_bias_pdf_params(index=index, value=value, **kwargs))

#  --- R PARAMETERS (constant and variable R)---

def _rt_params(initial_index=None, final_index=None, **kwargs):
    """Parameters for the probability density function (pdf) for 
    a single (constant) reproductive number.
    
    Parameters
    ----------
    initial_index : int
        Initial index of timeseries to consider. Pass 'None' if
        the R value is fixed over the simulation, or time varying.
    final_index : int
        Final index of timeseries to consider - given by the current index
        of the timeseries in the case of time-varying Rt. Pass 'None' if
        the R value is fixed over the time period.
    kwargs : Unpacked dict
        Unpacked collection of parameters objects
        
    Returns
    -------
    dict : Parameters for the conditional posterior used in sampling
    """
    params = kwargs

    if final_index is None:  # For single R0 case - considers whole timeseries
        window_start = 0
    elif initial_index is not None:  # For constant Rt over between given indices
        window_start = initial_index
    else:  # To compute params for a single index of a time varying Rt 
        window_start = max(0, final_index-params['Rt_window'])  # Typically -7 for one week
        final_index += 1  # So range includes current value

    unsorted_indicies = [int(k[len('data_'):]) for k in params.keys() if k.startswith('data_')]
    data_indicies = [k for k in sorted(unsorted_indicies)]
    truth_values = []; gamma_values = []

    for i in data_indicies[window_start:final_index]:
        gamma_values.append(_calculate_lambda(params, i))
        try:
            truth_values.append(params['truth_' + str(i)])
        except KeyError:
            truth_values.append(int(params['data_' + str(i)]
                                    / params['bias_' + str(i % 7)]))

    gamma_params = {'a': params['rt_prior_alpha'] + sum(truth_values),
                   'scale': 1 / (params['rt_prior_beta'] + sum(gamma_values))
                   }  # scale is inverse of beta value
    
    return gamma_params

def single_r_parameter(value, sampling_freq = 1):
    """Parameters for the probability density function (pdf) for 
    a single (constant) reproductive number.
    
    Parameters
    ----------
    value : int
        Initial value for this parameter object
    sampling_freq : int
        Will sample this parameter 1 in every 'sampling_freq' iterations - 
        defaults to unity (i.e. sampling every iteration)
    
    Returns
    -------
    GibbsParameter : Parameter object for constant reproductive number    
        """
    return GibbsParameter(value=value, conditional_posterior=ss.gamma.rvs, sampling_freq=sampling_freq,
                            posterior_params=lambda **kwargs : _rt_params(final_index=None, **kwargs))

def constant_r_parameter(value, start, end, sampling_freq = 1):
    """Parameters for the probability density function (pdf) for 
    a constant reproductive number between two indexes of a timeseries.
    
    Parameters
    ----------
    value : int
        Initial value for this parameter object
    sampling_freq : int
        Will sample this parameter 1 in every 'sampling_freq' iterations - 
        defaults to unity (i.e. sampling every iteration)
    
    Returns
    -------
    GibbsParameter : Parameter object for constant reproductive number    
        """
    return GibbsParameter(value=value, conditional_posterior=ss.gamma.rvs, sampling_freq=sampling_freq,
                            posterior_params=lambda **kwargs : _rt_params(initial_index=start,
                                                                          final_index=end, **kwargs))

def rt_parameter(value, index, sampling_freq = 1):
    """Parameters for the probability density function (pdf) for 
    one index of the time-varying reproductive number.
    
    Parameters
    ----------
    value : int
        Initial value for this parameter object
    index : int
        Index of the timeseries to which this Rt value corresponds
    sampling_freq : int
        Will sample this parameter 1 in every 'sampling_freq' iterations - 
        defaults to unity (i.e. sampling every iteration)
    
    Returns
    -------
    GibbsParameter : Parameter object for constant reproductive number    
        """
    return GibbsParameter(value=value, conditional_posterior=ss.gamma.rvs, sampling_freq=sampling_freq,
                          posterior_params=lambda **kwargs : _rt_params(final_index=index, **kwargs))