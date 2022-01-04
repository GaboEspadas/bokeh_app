import numpy as np
import pandas as pd
from bokeh.events import Pan
from bokeh.layouts import column, gridplot
from bokeh.models import PointDrawTool, ColumnDataSource, Panel, MonthsTicker, RangeTool, \
    NumeralTickFormatter, HoverTool, Select
from bokeh.models import Range1d
from bokeh.plotting import figure


def edit_time_series(df_in: pd.DataFrame):
    df_parsed = df_in.copy()

    # Families and colors
    available_families = list(set(df_parsed['family']))
    available_families.sort()
    df_parsed['original_sales'] = df_parsed['sales'].copy()
    df_parsed['original_date'] = df_parsed['date'].copy()

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

    def make_dataset_for_hist(data):
        # Create a histogram with 5 minute bins
        arr_hist, edges = np.histogram(data['sales'], bins=20)

        # Divide the counts by the total to get a proportion
        arr_df = pd.DataFrame(
            {'proportion': arr_hist / np.sum(arr_hist), 'left': edges[:-1], 'right': edges[1:]})

        # Format the proportion
        arr_df['f_proportion'] = ['%0.5f' % proportion for proportion in arr_df['proportion']]

        # Overall dataframe
        arr_df = arr_df.sort_values(['left'])

        return ColumnDataSource(arr_df)

    def make_layout(src, title):
        src_hist = make_dataset_for_hist(src.to_df())
        p = figure(x_axis_type="datetime",
                   title='',
                   # y_range=Range1d(0, limit_y),
                   x_range=Range1d(min(src.data['date']),
                                   max(src.data['date'])),
                   plot_width=1000,
                   plot_height=300,
                   outline_line_color="black",
                   background_fill_color="#deebf7",
                   name='main_plot'
                   )
        p.title.text = title

        # Original Sales
        p.circle(x='original_date',
                 y='original_sales',
                 source=src,
                 size=5,
                 legend_label='Original Sales',
                 fill_color="gray",
                 fill_alpha=.4)
        p.line(x='original_date',
               y='original_sales',
               source=src,
               line_width=2,
               legend_label='Original Sales',
               line_color="blue",
               line_alpha=.2)

        # Sales to be adjusted
        p.line(x='date',
               y='sales',
               source=src,
               line_width=2,
               legend_label='Adjusted Sales')
        renderer = p.circle(x='date',
                            y='sales',
                            source=src,
                            size=5,
                            legend_label='Adjusted Sales',
                            # set visual properties for selected glyphs
                            selection_color="firebrick",
                            # set visual properties for non-selected glyphs
                            nonselection_fill_alpha=0.2,
                            nonselection_fill_color="grey",
                            nonselection_line_color="firebrick",
                            nonselection_line_alpha=1.0)
        draw_tool = PointDrawTool(renderers=[renderer], add=False)
        p.add_tools(draw_tool)
        p.toolbar.active_tap = draw_tool  # Set as default

        hover = HoverTool(tooltips=[('Month', '$x{%b %Y}'),
                                    ('Original Sales', '@original_sales{(0 a)}'),
                                    ('Adjusted Sales', '@sales{(0 a)}')],
                          formatters={'$x': 'datetime'}
                          )

        p.add_tools(hover)

        # Styling
        p = style(p)

        p.add_layout(p.legend[0], 'right')

        # Add second plot
        select = figure(height=50,
                        width=1000,
                        # y_range=p.y_range,
                        x_axis_type="datetime",
                        y_axis_type=None,
                        tools="",
                        toolbar_location=None,
                        sizing_mode="scale_width")

        range_tool = RangeTool(x_range=p.x_range)
        range_tool.overlay.fill_color = "navy"
        range_tool.overlay.fill_alpha = 0.2

        select.line(x='date', y='sales', source=src)

        select.add_tools(range_tool)
        select.toolbar.active_multi = range_tool

        # Style for the select
        select.ygrid.grid_line_color = None
        select.toolbar.active_multi = range_tool
        select.background_fill_color = "#f5f5f5"
        select.grid.grid_line_color = "white"
        select.x_range.range_padding = 0.1

        # Selection
        select_family = Select(options=available_families,
                               width=200,
                               title='Family',
                               value=available_families[0])

        # Histogram
        hp = figure(width=200,
                    height=p.height,
                    y_range=p.y_range,
                    toolbar_location=None,
                    title='Histogram Sales',
                    x_axis_label='Proportion',
                    y_axis_label='Sales buckets')

        hp.xaxis.axis_label_text_font_size = '8pt'
        hp.xaxis.axis_label_text_font_style = 'bold'
        hp.yaxis.axis_label_text_font_size = '8pt'
        hp.yaxis.axis_label_text_font_style = 'bold'

        # Quad glyphs to create a histogram
        hp.quad(source=src_hist,
                left='proportion',
                right=0,
                bottom='left',
                top='right',
                fill_alpha=0.7,
                hover_fill_color='color',
                hover_fill_alpha=1.0,
                line_color='black'
                )
        hp.toolbar.logo = None
        hp.yaxis[0].formatter = NumeralTickFormatter(format="0 a")
        hp.xaxis[0].formatter = NumeralTickFormatter(format="0.0%")
        hp.xgrid.grid_line_color = None
        hp.xaxis.major_label_orientation = np.pi / 4
        hp.background_fill_color = "#fafafa"

        hover_h = HoverTool(tooltips=[('Bucket', '@left{(0 a)} - @right{(0 a)}'),
                                      ('Proportion', '@f_proportion{0.0%}')])
        hp.add_tools(hover_h)

        # Callbacks
        def update_data(wttr, old, new):
            p.title.text = f'Sales History for {new}'
            new_src = get_dataset(new)
            src.update(data=dict(new_src.data))
            range_tool.update(x_range=p.x_range)

            # Hist
            new_src_hist = make_dataset_for_hist(new_src.to_df())
            src_hist.update(data=dict(new_src_hist.data))

        def restore_date_coordinate(event):
            patches = {
                'date': [(slice(None), src.data['original_date'])],
            }
            src.patch(patches)
            # Hist
            new_src_hist = make_dataset_for_hist(src.to_df())
            src_hist.update(data=dict(new_src_hist.data))

        p.on_event(Pan, restore_date_coordinate)

        select_family.on_change('value', update_data)

        full_plot = gridplot([[hp, p], [None, select]], merge_tools=False)
        layout = column(select_family, full_plot)

        return layout

    def get_dataset(family_selected):
        df_selected = df_parsed.query(f'family=="{family_selected}"').copy().reset_index()
        return ColumnDataSource(df_selected)

    initial_source = get_dataset(available_families[0])
    plot = make_layout(initial_source, f'Time Series for {available_families[0]}')
    tab = Panel(child=plot, title='Edit Time Series')
    return tab
