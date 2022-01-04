import pandas as pd
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

from compare_time_series import compare_time_series
from edit_time_series import edit_time_series

df = pd.read_csv('time_series_viz/data/train.csv')
df['date'] = pd.to_datetime(df['date'])
df_g = df.groupby(pd.Grouper(key='date', freq='1M'))[['sales']].sum().reset_index().head(100)
df_g['original_sales'] = df_g['sales'].copy()
df_family = df.groupby(['family', pd.Grouper(key='date', freq='1M')])[['sales']].sum().reset_index()

tab1 = edit_time_series(df_family)
tab2 = compare_time_series(df_family)
tabs = Tabs(tabs=[tab1, tab2])
curdoc().add_root(tabs)
