import pandas as pd
from bokeh.layouts import row, column
from bokeh.models import (ColumnDataSource, Panel, HoverTool, NumeralTickFormatter)
from bokeh.models import MonthsTicker
from bokeh.models.widgets import (CheckboxGroup)
from bokeh.palettes import Spectral11
from bokeh.plotting import figure




def compare_time_series(df_sales: pd.DataFrame):
    def make_dataset(family_list):
        if not family_list:
            family_list = df_sales['family'].values[0:1]
        families_selected = df_sales[df_sales['family'].isin(family_list)].copy()
        xs = []
        ys = []
        legends = []
        for f, df in families_selected.groupby('family'):
            xs.append(df['date'])
            ys.append(df['sales'])
            legends.append(f)
        color = Spectral11[:len(legends)]
        data = {'date': xs, 'sales': ys, 'family': legends, 'color': color}

        return ColumnDataSource(data)

    def style(p):
        # Title
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'

        # High level
        p.grid.grid_line_color = "white"
        p.toolbar.logo = None

        # Axis titles
        p.yaxis.axis_label = 'Sales'
        p.xaxis.axis_label_text_font_size = '8pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '8pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '8pt'
        p.xaxis.formatter.days = '%b %Y'
        p.xaxis[0].ticker = MonthsTicker(months=[3, 6, 9, 12])
        p.yaxis.major_label_text_font_size = '8pt'
        p.yaxis[0].formatter = NumeralTickFormatter(format="0 a")

        return p

    def make_plot(src):
        # Blank plot with correct labels
        p = figure(x_axis_type="datetime",
                   title='Sales per Family',
                   plot_width=1000,
                   plot_height=400,
                   outline_line_color="black",
                   background_fill_color="#deebf7")

        p.multi_line(xs='date',
                     ys='sales',
                     legend='family',
                     line_width=1,
                     color='color',
                     source=src)

        # Styling
        p = style(p)
        p.add_layout(p.legend[0], 'right')
        hover = HoverTool(tooltips=[('Month', '$x{%b %Y}'),
                                    ('Family', '@family'),
                                    ('Sales', '$y{(0 a)}')],
                          formatters={'$x': 'datetime'}
                          )

        p.add_tools(hover)
        return p

    def update(attr, old, new):
        families_to_plot = [family_selection.labels[i] for i in family_selection.active]

        new_src = make_dataset(families_to_plot)

        src.data.update(new_src.data)

    # Families and colors
    available_families = list(set(df_sales['family']))
    available_families.sort()

    family_selection = CheckboxGroup(labels=available_families,
                                     width=200,
                                     active=[0, 1])
    family_selection.on_change('active', update)

    # Initial carriers and data source
    initial_carriers = [family_selection.labels[i] for i in family_selection.active]

    src = make_dataset(initial_carriers)
    p = make_plot(src)

    # Put controls in a single element
    controls = column(family_selection)

    # Create a row layout

    layout = row(controls, p)

    # Make a tab with the layout
    tab = Panel(child=layout, title='Compare Time Series')

    return tab
