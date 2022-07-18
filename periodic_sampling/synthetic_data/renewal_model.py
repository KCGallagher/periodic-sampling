#
# Simulation class for a renewal model
#

import numpy as np
import pandas as pd
import scipy.stats as ss
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = '12'


class RenewalModel():
    """Simulator class for a Renewal Model"""

    def __init__(self, R0 = 1) -> None:
        self.reproduction_num = R0
        self.serial_interval = self.calc_serial_interval()

    def calc_serial_interval(self, mu = 4.7, sigma = 2.9, days=20):
        """Generates a discrete serial interval distribution,
        based on a continuous lognormal distribution.
        
        Default parameter values taken from Nishiura et al. (2020)
        https://doi.org/10.1016/j.ijid.2020.02.060
        """
        dist = ss.lognorm(s=np.log(sigma), scale=mu)
        unnorm_values = dist.pdf(range(days))
        return unnorm_values / sum(unnorm_values)
        
    def simulate(self, T, N_0):
        """Simulate renewal model over T steps,
        with N_0 initial cases."""
        self.t_step = T
        self.N_0 = N_0

        omega = self.serial_interval
        cases = [N_0]
        for t in range(1, T):
            n_terms_gamma = min(t + 1, len(omega))  # Number of terms in sum for gamma
            gamma = sum([omega[i] * cases[-i] for i in range(1, n_terms_gamma)])
            cases.append(np.random.poisson(self.reproduction_num * gamma))
        self.case_data = cases

    def report(self, output_loc):
        """Save data to .csv format compatible with
        John Hopkins Covid Data"""
        df = pd.DataFrame(self.case_data, columns = ['Confirmed'])
        # Include date column based on start date provided
        # Include death data based on fatality rate provided
        df.to_csv(output_loc)

    def plot(self, save_loc = None):
        """Plot case data over time"""
        plt.plot(range(len(self.case_data)), self.case_data)
        plt.xlabel("Days"); plt.ylabel("Cases")
        plt.tight_layout()
        if save_loc is not None:
            name = f"synthetic_cases_T_{self.t_step}_N0_{self.N_0}.png"
            plt.savefig(save_loc + name)
        else:
            plt.show()
        

model = RenewalModel(R0=0.99)
model.simulate(1000, 500)
model.report('test.csv')
model.plot()
