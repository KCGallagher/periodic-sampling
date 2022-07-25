#
# Classes for the Metropolis-Hastings sampler
#

import math
import random
import numpy as np
import pandas as pd
import scipy.stats as ss


class MetropolisParameter(float):
    """Parameter object for Metropolis sampler.
    """
    def __new__(cls, value, **kwargs):
        """Inherits from float class, so instances of Parameter will be treated as a
        float (of value self.value) in all arithmetic operations."""
        return super(MetropolisParameter, cls).__new__(cls, value)

    def __init__(self, value, step_size, prior, likelihood):
        """Constructor method of parameter object.
        
        Parameters
        ----------
        value : float
            The initial value of the parameter.
        step_size : float
            Step size used to propose new values for this parameter.
        prior : func
            Function object that returns pdf from prior distribution - 
            should be a lambda function that only requires value of parameter
            (i.e. other arguments for the prior distribution are preloaded.)
        likelihood : func
            Function object that returns pdf from likelihood distribution - 
            should be a lambda function that only requires value of parameter
            (i.e. other arguments for the prior distribution are preloaded.)

        """
        self.value = value
        self.step_size = step_size
        self.prior = prior
        self.likelihood = likelihood

        # Default proposal functions - can be redefined for Metropolis Hastings

        #   Function to sample from distribution (to propose new value)
        self.proposal_value = lambda loc : ss.norm.rvs(loc, scale=step_size)

        #   Function to generate pdf (for J(theta_1 | theta_2) in acceptance prob)
        #      Should be of the form f(x, y) to calculate P(x | y)
        self.proposal_func = lambda x, loc : ss.norm.pdf(x, loc, scale=step_size)


    def __str__(self) -> str:
        """String representation of object.
        
        Returns
        -------
        str
            Description of Parameter object
        """
        return (f"Metropolis Parameter of value {self.value}")


class MetropolisSampler:
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

    def _acceptance_decision(self, param, old_value, new_value):
        """Determines whether to accept a given proposed value, compared to
        the old value.
        
        Parameters
        ----------
        param : MetropolisParameter
            Parameter object, with methods to determine the prior, likelihood,
            and the proposal function (default is normally distributed).
        old_value : float
            Old value of parameter from previous sample.
        new_value : float
            Proposed new value of parameter, to be considered for next sample.

        Returns
        -------
        float : Sampled value of parameter to take forward
            (out of [old_value, new_value]).
        """
        old_posterior = param.prior(old_value) * param.likelihood(old_value)
        new_posterior = param.prior(new_value) * param.likelihood(new_value)

        hastings_correction = (param.proposal_func(old_value, new_value)
                               / param.proposal_func(new_value, old_value))

        r = min((new_posterior / old_posterior) * hastings_correction, 1)
        decision = math.floor(r + np.random.random())
        return [old_value, new_value][decision]

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
        assert isinstance(self.params[param_name], MetropolisParameter), \
            "Parameter name supplied must correspond to Parameter instance"
        old_value = self.params[param_name].value
        proposed_value = self.params[param_name].proposal_value(old_value)
        value = self._acceptance_decision(self.params[param_name],
                                         old_value, proposed_value)
        self.params[param_name].value = value
        return value

    def sampling_routine(self, step_num, sample_period = 1, sample_burnin = 0):
        """Conducts N iterations of a Metropolis-Hastings Sampler.
        
        Parameters
        ----------
        step_num : int
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
        for n in range(step_num):
            row = {}
            for key in list(params.keys()):
                if isinstance(params[key], MetropolisParameter):
                    row[key] = self.single_sample(key)
            if ((n >= sample_burnin) & (n % sample_period == 0)):
                history.append(row)
        return pd.DataFrame(history)