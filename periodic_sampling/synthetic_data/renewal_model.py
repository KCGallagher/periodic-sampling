#
# Simulation class for a renewal model
#

import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import scipy.stats as ss
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = '12'


class RenewalModel():
    """Simulator class for a Renewal Model"""

    def __init__(self, R0 = 1.0) -> None:
        """Consutructor method for a Renewal Model
        
        Parameters
        ----------
        R0 : float
            The instantaneous reproductive number, constant
            over time across the pandemic
        """
        self.reproduction_num = R0
        self.serial_interval = self.calc_serial_interval()

    def calc_serial_interval(self, mu = 4.7, sigma = 2.9, days=20):
        """Generates a discrete serial interval distribution,
        based on a continuous lognormal distribution.
        
        Default parameter values taken from Nishiura et al. (2020)
        https://doi.org/10.1016/j.ijid.2020.02.060.

        Parameters
        ----------
        mu : float
            Mean of the lognormal distribution generating the serial interval
        sigma : float
            Standard deviation of the lognormal dist for the serial interval
        days : int
            Cutoff duration of serial interval

        Returns
        -------
        list : Discrete probability distribution for the serial interval
        """
        dist = ss.lognorm(s=np.log(sigma), scale=mu)
        unnorm_values = dist.pdf(range(days))
        return unnorm_values / sum(unnorm_values)
        
    def simulate(self, T, N_0):
        """Simulate renewal model over T steps, with N_0 initial cases.
        Excludes original value due to incomplete history.
        
        Parameters
        ----------
        T : int
            Number of steps (days) to simulate
        N_0 : int
            Number of initial cases for the renewal model
        """
        self.t_step = T
        self.N_0 = N_0

        omega = self.serial_interval
        cases = [N_0]
        for t in tqdm(range(1, T)):
            n_terms_gamma = min(t + 1, len(omega))  # Number of terms in sum for gamma
            gamma = sum([omega[i] * cases[-i] for i in range(1, n_terms_gamma)])
            cases.append(np.random.poisson(self.reproduction_num * gamma))
        self.case_data = pd.DataFrame(cases[1:], columns = ['Cases'])

    def plot(self, save_loc = None):
        """Plot case data over time.
        
        Parameters
        ----------
        save_loc : str
            File directory to save output image. If not specified,
            will show image instead of saving.
        """
        plt.plot(range(len(self.case_data)), self.case_data)
        plt.xlabel("Days"); plt.ylabel("Cases")
        plt.tight_layout()
        if save_loc is not None:
            name = f"synthetic_cases_T_{self.t_step}_N0_{self.N_0}.png"
            plt.savefig(os.path.join(save_loc, name))
        else:
            plt.show()
