#
# Classes for the Gibbs sampler
#

import random
import pandas as pd


class Parameter(float):
    """Parameter object for Gibbs sampler.
    """
    def __new__(cls, value, conditional_posterior, posterior_params = None):
        """Inherits from float class, so instances of Parameter will be treated as a
        float (of value self.value) in all arithmetic operations."""
        return super(Parameter, cls).__new__(cls, value)

    def __init__(self, value, conditional_posterior, posterior_params = None):
        """Constructor method of parameter object.
        
        Parameters
        ----------
        value : float
            The initial value of the parameter
        conditional_posterior : func
            Function object that returns random sample from known distribution
        posterior_params : func
            Function object that generates parameters for the conditional_
            posterior method - returns a dictionary. Optional - if not specified,
            the params dict will be fed directly into the conditional posterior
        """
        self.value = value
        self.conditional_posterior = conditional_posterior
        self.posterior_params = posterior_params

    def __str__(self) -> str:
        """String representation of object.
        
        Returns
        -------
        str
            Description of Parameter object
        """
        return (f"Parameter of value {self.value}, with {self.conditional_posterior.__name__} conditional posterior")

    def sample(self, sample_params):
        """Samples from the conditional posterior distribution.
        
        Parameters
        ----------
        sample_params : dict
            Dictionary of the all current parameter values, required
            to generate the shape of the posterior distribution.

        Returns
        -------
        float
            Value of parameter sampled from conditional posterior
        """
        if self.posterior_params is None:
            # Can directly feed params into conditional_posterior
            post_params = sample_params
        else:
            param_values = {}
            for k, v in sample_params.items():
                if isinstance(v, Parameter):
                    param_values[k] = v.value
                else:
                    param_values[k] = v
            post_params = self.posterior_params(**param_values)
        self.value = self.conditional_posterior(**post_params)
        return self.value


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