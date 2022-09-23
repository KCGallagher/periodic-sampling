#
# Collection of functions used for plotting bias
#

import numpy as np
import pandas as pd
import scipy as sp
import seaborn as sns

from .country_data import rel_reporting_calc

def fourier_transform(df, column, compute_psd = False):
    data = df[column].fillna(0).values
    data_fft = sp.fftpack.fft(data)
    data_psd = np.abs(data_fft) ** 2  # Power Spectral density

    fftfreq = sp.fftpack.fftfreq(len(data_fft), 1/7)  # Frequency units in weeks
    return (data_psd, fftfreq) if compute_psd else (data_fft, fftfreq)

def plot_fft(data, freq, ax, label, **kwargs):
    i = freq > 0  # Remove negative frequencies
    ax.plot(freq[i], 10 * np.log10(data[i]), label=label, **kwargs)
    y_lim = ax.get_ylim()
    ax.vlines([(n+1) for n in range(3)], y_lim[0], y_lim[1],
              colors='gray', linestyles='dashed', alpha=0.6)
    # ax.axvspan(0, 0.9, facecolor='gray', alpha=0.3)
    ax.set_xlabel('Frequency (1/week)')
    ax.set_ylabel('PSD (dB)')
    ax.legend(loc=3); ax.set_xlim((0, max(freq[i])))

def rel_reporting_box(daily_df, column, ax, color, label):
    daily_df = rel_reporting_calc(daily_df, [column])
    # daily_df['Dif_' + column].fillna(0, inplace=True)

    daily_df.boxplot(column=('Dif_' + column), by='Day_Index', # positions='DayIndex',
                     ax=ax, color=color, sym='')
    ax.set_xticks([1, 2, 3, 4, 5, 6, 7],
                  ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    ax.set_title(''); ax.legend(labels=[label], loc=1, framealpha=0.8)

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