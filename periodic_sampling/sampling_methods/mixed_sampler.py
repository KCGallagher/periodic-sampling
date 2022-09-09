#
# Classes for the Metropolis-Hastings sampler
#

import random
import pandas as pd
from tqdm import tqdm

from .gibbs_sampler import GibbsParameter, GibbsSampler
from .metropolis_sampler import MetropolisParameter, MetropolisSampler


class MixedSampler:
    """Sampling class allowing use of both Gibbs and Metropolis
    methods depedant on the parameter type."""

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


    def sampling_routine(self, step_num, sample_period = 1,
                         sample_burnin = 0, random_order = False, chain_num = None):
        """Conducts repeated sampling iterations using either the Gibbs or 
        Metropolis-Hastings methods.
        
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
        random_order : bool
            Where to update Parameters in a random order, or simply use
            the order in which they were listed in the dictionary
        chain_num : int
            If this is specified, will record the chain number in output 
            Dataframe for use in analysis
        """
        metropolis = MetropolisSampler(self.params)
        gibbs = GibbsSampler(self.params)

        params = self.params
        history = []
        for n in tqdm(range(step_num)):
            row = {}
            if random_order:
                random.shuffle(list(params.keys()))
            for key in list(params.keys()):
                if isinstance(params[key], MetropolisParameter):
                    if n % params[key].sampling_freq == 0:
                        metropolis.params = self.params  # Resync with global params
                        row[key] = metropolis.single_sample(key)
                        self.params[key].value = row[key]  # Update global params
                elif isinstance(params[key], GibbsParameter):
                    if n % params[key].sampling_freq == 0:
                        gibbs.params = self.params
                        row[key] = gibbs.single_sample(key)
                        self.params[key].value = row[key]

            bias_sum = sum([row[key] for key in params.keys() if (key.startswith('bias_') and not key.startswith('bias_prior'))])
            
            # for key in list(params.keys()):
            #     if key.startswith('bias_') and not key.startswith('bias_prior'):
            #         row[key] /= (bias_sum / 7)
            #         self.params[key].value = row[key]

            # random_bias = 'bias_' + str(random.randint(0, 6))
            # row[random_bias] = max(0.01, 7 - (bias_sum - row[random_bias]))
            # self.params[random_bias].value = row[random_bias]

            while abs(bias_sum - 7) > params['error_threshold_bias']: 
                for key in list(params.keys()):
                    if isinstance(params[key], GibbsParameter):  # resample both bias and Rt 
                        gibbs.params = self.params
                        row[key] = gibbs.single_sample(key)
                        self.params[key].value = row[key]
                bias_sum = sum([row[key] for key in params.keys() if (key.startswith('bias_') and not key.startswith('bias_prior'))])


            if (((n + 1) > sample_burnin) & ((n + 1) % sample_period == 0)):
                if chain_num is not None:
                    row['Chain'] = chain_num
                history.append(row)

        return pd.DataFrame(history)
