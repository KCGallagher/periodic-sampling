#
# Methods for the Gibbs sampler
#

import random
import pandas as pd

from gibbs_param import Parameter

def gibbs_sampler(N, params):
    """Conducts N iterations of a Gibbs Sampler.
    
    params: Dictionary of all parameters + constants required for 
        calculating conditional posterior distributions
    """
    history = []
    for _ in range(N):
        row = {}
        random.shuffle(list(params.keys()))
        for key in list(params.keys()):
            if isinstance(params[key], Parameter):
                value = params[key].sample(params)
                params[key].value = value
                row[key] = value
        history.append(row)
    return pd.DataFrame(history)