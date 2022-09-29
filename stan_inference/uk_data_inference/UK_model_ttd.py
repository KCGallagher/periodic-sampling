#
# Inference code, using same format api as in `phe_api.py`. 
# Includes time to death delay as a gamma distribution
#

import stan
import numpy as np
import pandas as pd
import scipy.stats as ss
from uk_covid19 import Cov19API

from periodic_sampling.synthetic_data import RenewalModel


def retrieve_death_data(area_name, area_type):
  """Get the Covid data via the API"""
  try:  
    location_filter = [f'areaType={area_type}',
    f'areaName={area_name}']

    # The metric(s) to request
    req_structure = {
        "date": "date",
        "areaCode": "areaCode",
        "newDeaths28DaysByDeathDate": "newDeaths28DaysByDeathDate",
        "newDeaths28DaysByPublishDate": "newDeaths28DaysByPublishDate",
        }

    api = Cov19API(filters=location_filter, structure=req_structure)

    data = api.get_json()
    return data['data']

  except Exception as ex: 
    print(f'Exception [{ex}]')


data = retrieve_death_data(area_name='england', area_type='nation')
uk_df = pd.DataFrame(data); uk_df.to_csv("stan_inference/uk_data_inference/input_data.csv")
uk_df["Date"] = pd.to_datetime(uk_df["date"], format = "%Y-%m-%d")
uk_df.sort_values(by="Date", inplace=True);
uk_df = uk_df[uk_df["Date"] < "2022-02-01"]

with open("stan_inference/uk_data_inference/UK_model_ttd.stan") as f:
    fixed_bias_code = f.read()

# Preprocessing to remove nan and zero values (invalid under renewal model framework)
c_val = uk_df['newDeaths28DaysByPublishDate'].values
c_val = np.nan_to_num(c_val, nan=0).astype(int)
np.place(c_val, c_val<1, [1])

# Discrete gamma delay dist
vals = [ss.gamma.pdf(x, a = 2.5, scale = 1/0.14) for x in range(60)]
vals[0] = 1e-4  # Prevent division by zero error

fixed_bias_data = {
    "time_steps": len(c_val),
    "C": list(c_val),
    "Rt_window": 7,
    "serial_interval": RenewalModel(R0=None).serial_interval,
    "gamma_delay": vals / sum(vals),
    "alpha_prior": [1 for _ in range(7)],  # larger val -> tighter dist
    "death_time_dist_alpha": 2.5,
    "death_time_dist_beta": 0.14
}

posterior = stan.build(fixed_bias_code, data=fixed_bias_data, random_seed=1) 

chain_num = 1
sample_num = int(5)
bias_init_val = [1/7 for _ in range(7)]  # ((i+1)/28) for simplex step
rt_init_val = [1 for _ in range(fixed_bias_data['time_steps'])]
init_values = [{'alpha': bias_init_val, 'R': rt_init_val} for _ in range(chain_num)] 

fit = posterior.sample(num_chains=chain_num, num_samples=sample_num, 
                       num_thin=int(1),
                       init=init_values,
                       )
df = fit.to_frame()
df = df[df.columns.drop([c for c in df.columns if c.startswith('alpha')])]
print(df.describe().T)

filename = f"stan_inference_ttd_UK_newDeaths28DaysByPublishDate_It_{sample_num}_chains_{chain_num}.csv"
df.to_csv("stan_inference/uk_data_inference/" + filename)

