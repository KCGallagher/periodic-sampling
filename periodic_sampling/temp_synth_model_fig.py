# Imports

import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = '12'

from datetime import datetime

from synthetic_data import RenewalModel, Reporter
from analysis import rel_reporting_calc


def rel_reporting_violin(daily_df, value_cols, ax, cutoff, colors, labels):
    for column in value_cols:
        daily_df = rel_reporting_calc(daily_df, [column])

    id_col = list(daily_df.columns.values)
    for i, value in enumerate(value_cols):
        value_cols[i] = 'Dif_' + value
        id_col.remove('Dif_' + value)
    violin_df = pd.melt(daily_df, id_vars = id_col, value_vars=value_cols, var_name='Type')
    ax.hlines(y=1, xmin=-1, xmax=7, linestyles="dashed", color="gray")

    #N.B exclude zero values from discrete nature of data - distorts violin
    sns.violinplot(data=violin_df, y=violin_df[(violin_df['value']<cutoff) & (violin_df['value']>0)]['value'],
                   ax=ax, x='Weekday', hue='Type', palette=colors, saturation=0.9, split=True, inner='quartile',# cut=0,
                   order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    ax.set_title(''); ax.set_xlim(-0.5,6.5)
    ax.legend(handles=ax.legend_.legendHandles, labels=labels)


# Import/Generate Data

input_dir = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
output_dir = "data/"
location_key = "England, United Kingdom"
location = re.sub('\W+','',location_key)

df = pd.read_csv(output_dir + location + ".csv")
df["Date"] = pd.to_datetime(df["Date"], format = "%Y-%m-%d")
df.sort_values(by="Date", inplace=True)

df["Daily_Deaths"] = df["Deaths"].diff()
df["Daily_Cases"] = df["Confirmed"].diff()

df[["Daily_Deaths","Daily_Cases"]] = df[["Daily_Deaths","Daily_Cases"]].clip(lower = 0)

df["Days"] = df["Date"].apply(lambda date: (date - min(df["Date"])).days)
df = rel_reporting_calc(df, ['Daily_Cases', 'Daily_Deaths'])

# Simulate Renewal Model
time_steps = 3000
N_0 = 40

np.random.seed(31)
model = RenewalModel(R0=0.999)
model.simulate(T=time_steps, N_0=N_0)

# Report unbiased and biased data

rep = Reporter(model.case_data)
truth_df = rep.unbiased_report()
bias_df = rep.fixed_bias_report(bias = [0.4, 1.5, 1.3, 1.1, 1.1, 1.1, 0.5],
                                method = 'poisson')

bias_df['Date'] = bias_df['Date'].apply(lambda t: datetime.combine(t, datetime.min.time()))
df2 = rel_reporting_calc(bias_df, ['Confirmed', 'Ground Truth'])

fig, axs = plt.subplots(1, figsize=(8,4))
rel_reporting_violin(df2.copy(), ['Ground Truth', 'Confirmed'],  ax=axs, cutoff=2,
                     colors=['black', 'tab:blue'], labels=["Ground Truth", "Weekly Bias"])  

fig.patch.set_facecolor('white')  # Overrides VSCode dark mode default
plt.xlabel('Weekday'); plt.ylabel("Reporting Factor")
plt.suptitle(''); plt.tight_layout(); plt.close()
# plt.savefig("../images/synthetic_data_examples/"
#             + f"biased_violin_T_{time_steps}_N0_{N_0}.png")

fig, axs = plt.subplots(1, figsize=(8,4))
x = rel_reporting_violin(df.copy(), ['Daily_Cases', 'Daily_Deaths'],  ax=axs, cutoff=2,
                   colors=['tab:blue', 'tab:red'], labels=["Cases", "Deaths"])  
print(x)

plt.xlabel('Weekday'); plt.ylabel("Reporting Factor")
plt.suptitle(''); plt.tight_layout(); plt.close()
# plt.savefig(f"../images/data_trends/daily_violin_{location}.png")

### Actual plotting
comb_df = pd.DataFrame(df[['Dif_Daily_Deaths', 'Weekday']])
comb_df.rename(columns={'Dif_Daily_Deaths': 'True_Deaths'} ,inplace=True)
comb_df = pd.concat([comb_df, df2[['Dif_Confirmed', 'Weekday']]], axis=0)
comb_df.rename(columns={'Dif_Confirmed': 'My_Deaths'} ,inplace=True)

value_cols = ['True_Deaths', 'My_Deaths']
for column in value_cols:
    mean = comb_df[column].rolling(7).mean()
    comb_df['Dif_' + column] = comb_df[column] / mean

id_col = list(comb_df.columns.values)
for i, value in enumerate(value_cols):
    value_cols[i] = 'Dif_' + value
    id_col.remove('Dif_' + value)
violin_df = pd.melt(comb_df, id_vars = id_col, value_vars=value_cols, var_name='Type')


fig, ax = plt.subplots(1, figsize=(8,4))
ax.hlines(y=1, xmin=-1, xmax=7, linestyles="dashed", color="gray")

#N.B exclude zero values from discrete nature of data - distorts violin
sns.violinplot(data=violin_df, y=violin_df[(violin_df['value']<2) & (violin_df['value']>0)]['value'],
            ax=ax, x='Weekday', hue='Type', palette=['tab:red', 'purple'], saturation=0.9, split=True, inner='quartile',
            order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
ax.set_title(''); ax.set_xlim(-0.5,6.5); ax.set_ylabel(r'$\alpha_{i}$')
ax.legend(handles=ax.legend_.legendHandles, labels=["UK deaths", "Synthetic"])
plt.savefig("images/synthetic_data_examples/"
            + f"comparison_violin_T_{time_steps}_N0_{N_0}.png")
plt.show()
