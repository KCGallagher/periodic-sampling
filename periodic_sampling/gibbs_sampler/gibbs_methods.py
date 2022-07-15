#
# Methods for the Gibbs sampler
#

import random
import pandas as pd

from gibbs_param import Parameter

def gibbs_sampler(N, params, sample_period = 1, sample_burnin = 0):
    """Conducts N iterations of a Gibbs Sampler.
    
    params: Dictionary of all parameters + constants required for 
        calculating conditional posterior distributions. Parameters 
        that will be updated should be instances of the Parameter class.
    sample_period: How frequently to record samples - as successive
        samples have some degree of correlation (forming a Markov Chain)
    sample_burnin: Interations before recording, to allow the stationary
        distribution to be reached
    """
    history = []
    for n in range(N):
        row = {}
        random.shuffle(list(params.keys()))
        for key in list(params.keys()):
            if isinstance(params[key], Parameter):
                value = params[key].sample(params)
                params[key].value = value
                row[key] = value
        if ((N >= sample_burnin) & (N % sample_period == 0)):
            history.append(row)
    return pd.DataFrame(history)