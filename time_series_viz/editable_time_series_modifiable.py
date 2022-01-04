# pandas and numpy for data manipulation
from math import pi

from bokeh.layouts import row, WidgetBox
from bokeh.models import (HoverTool,
                          ColumnDataSource, Panel, BasicTickFormatter, Range1d, PointDrawTool)
from bokeh.models import MonthsTicker
from bokeh.models.widgets import (CheckboxGroup)
from bokeh.plotting import figure


def editable_time_series_tab(df_sales):
    def make_dataset(family_list):
        families_selected = df_sales[df_sales['family'].isin(family_list)].copy()
        xs = []
        ys = []
        legends = []
        for f, df in families_selected.groupby('family'):
            xs.append(df['date'])
            ys.append(df['sales'])
            legends.append(f)
        data = {'xs': xs, 'ys': ys, 'legend': legends}

        return ColumnDataSource(data)

    def style(p):
        # Title
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'

        # Axis titles
        p.xaxis.major_label_orientation = pi / 4
        p.xaxis.formatter.days = '%m-%Y'
        p.toolbar.logo = None
        p.xaxis[0].ticker = MonthsTicker(months=list(range(1, 13)))

        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'
        p.yaxis.formatter = BasicTickFormatter(use_scientific=False)

        return p

    def make_plot(src):
        # Blank plot with correct labels


        p = figure(x_axis_type="datetime",
                   title='Sales per store',
                   plot_width=1200, plot_height=300)

        p.circle(x='date', y='sales',
                 source=df,
                 size=4,
                 legend_label='original sales',
                 fill_color="gray",
                 fill_alpha=.4)
        p.line(x='date', y='sales',
               source=df,
               line_width=2,
               legend_label='original sales',
               line_color="blue",
               line_alpha=.2)

        p.line(x='date', y='sales', source=src, line_width=2, legend_label='sales')
        modifiable_circles = p.circle(x='date', y='sales', source=src, size=4, legend_label='sales')

        draw_tool = PointDrawTool(renderers=[modifiable_circles], add=False)
        p.add_tools(draw_tool)

        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('Family', '@family'),
                                    ('Sales', '@sales')],
                          mode='vline')

        p.add_tools(hover)

        # Styling
        p = style(p)

        return p

    def update(attr, old, new):
        families_to_plot = [family_selection.labels[i] for i in family_selection.active]

        new_src, _ = make_dataset(families_to_plot)

        src.data.update(new_src.data)

    # Families and colors
    available_families = list(set(df_sales['family']))
    available_families.sort()

    family_selection = CheckboxGroup(labels=available_families,
                                     active=[0, 1])
    family_selection.on_change('active', update)

    # Initial carriers and data source
    initial_carriers = [family_selection.labels[i] for i in family_selection.active]

    src, df = make_dataset(initial_carriers)
    p = make_plot(src, df)

    # Put controls in a single element
    controls = WidgetBox(family_selection)

    # Create a row layout
    layout = row(controls, p)

    # Make a tab with the layout
    tab = Panel(child=layout, title='Edit Time Series')

    return tab
