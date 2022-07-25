#
# Methods for the Gibbs sampler
#

import random
import pandas as pd

from gibbs_param import Parameter

class GibbsSampler:
    """Sampling class using Gibbs methods"""

    def __init__(self, params):
        """Constructor object, takes dictionary of parameters
        
        Parameters
        ----------
        params : Dict
            Dictionary of all parameters + constants required for 
            calculating conditional posterior distributions. Parameters 
            that will be updated should be instances of the Parameter class.
        """
        self.params = params

    def single_sample(self, param_name):
        """Runs single sample of a parameter, updating the value 
        inplace in the params dictionary and returning the updated value
        for recording.
        
        Parameters
        ----------
        param_name : str
            Key from params dictionary corresponding to Parameter
            instance to sample from.
        """
        assert isinstance(self.params[param_name], Parameter), \
            "Parameter name supplied must correspond to Parameter instance"
        value = self.params[param_name].sample(self.params)
        self.params[param_name].value = value
        return value

    def sampling_routine(self, N, sample_period = 1, sample_burnin = 0):
        """Conducts N iterations of a Gibbs Sampler.
        
        Parameters
        ----------
        N : int
            Number of iterations to sample over
        sample_period : int
            How frequently to record samples - as successive
            samples have some degree of correlation (forming a Markov Chain)
        sample_burnin : int
            Interations before recording, to allow the stationary
            distribution to be reached
        """
        params = self.params
        history = []
        for n in range(N):
            row = {}
            random.shuffle(list(params.keys()))
            for key in list(params.keys()):
                if isinstance(params[key], Parameter):
                    row[key] = self.single_sample(key)
            if ((n >= sample_burnin) & (n % sample_period == 0)):
                history.append(row)
        return pd.DataFrame(history)