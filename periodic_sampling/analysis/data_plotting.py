#
# Collection of functions used for plotting bias
#

import pandas as pd
import seaborn as sns

from country_data import rel_reporting_calc


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