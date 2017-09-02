"""
* author: Gavin Hull
* version: 2017.08.22
* short description: Plot graphs of API calls with points for their start and end times.
* description: Here we are plotting a graph of its calls to APIs for each binary. We also process the calls to APIs per category,
as defined in the RanDep model, and plot their start and end times. This gives a graphical representation of how the
sample behaves according to the model.
Since the data has been processed by the report parser, we need to read the start and end time of each API per binary.
The axis are trace_start: x = start_times, y = apis; trace_end: x = end_times, y = apis;
"""

from plotly.offline import plot
import plotly.graph_objs as go
import re


class Plot(object):
    def __init__(self):
        pass

    @staticmethod
    def plots(_filename, apis, start_times, end_times):
        """Each binary has a filename, list of APIs, and each API has start and end times. These parameters are
        fed into this function to make two traces for start and end, where the x-axis is the list of times, and
        y-axis is the list of APIs"""

        # set the height of the graph based on the number of APIs
        api_len = len(apis) * 22
        g_height = api_len if api_len > 300 else 300
        # set the left margin based on the longest word
        l_margin = len(max(apis, key=len)) * 8

        if 'json' in _filename:
            regex = re.compile(r'^.*/(.*?)[\.|-]json')
            file_name = re.match(regex, _filename).group(1)
        elif '/' in _filename:
            regex = re.compile(r'^.*/(.*)$')
            file_name = re.match(regex, _filename).group(1)
        else:
            file_name = _filename

        dark_color = 'rgb(68,68,68)'
        light_color = 'rgb(255,255,255)'
        dark_color_trans = 'rgba(68,68,68,0.75)'
        light_color_trans = 'rgba(255,255,255,0.75)'
        trans = 'rgba(255,255,255,0.1)'

        trace0 = go.Scatter(
            x=start_times,
            y=apis,
            marker=dict(color=dark_color_trans,
                        line=dict(width=1,
                                  color=dark_color),
                        size=12),
            mode="markers",
            name="Start Time"
        )
        trace1 = go.Scatter(
            x=end_times,
            y=apis,
            marker=dict(color=light_color_trans,
                        line=dict(width=1,
                                  color=dark_color),
                        size=12),
            mode="markers",
            name="End Time"
        )

        data = [trace0, trace1]
        layout = go.Layout(title="%s's API Start and End Times" % file_name,
                           xaxis=dict(title="Time (s)",
                                      showgrid=True,
                                      showline=True,
                                      linecolor=dark_color_trans,
                                      titlefont=dict(color=dark_color),
                                      tickfont=dict(color=dark_color),
                                      autotick=False,
                                      dtick=10,
                                      ticks='outside',
                                      tickmode='auto',
                                      nticks=50,
                                      tickcolor=dark_color),
                           margin=dict(
                               l=l_margin,
                               r=40,
                               b=60,
                               t=80
                           ),
                           legend=dict(
                               font=dict(
                                   size=10,
                               ),
                               yanchor='bottom',
                               xanchor='right',
                           ),
                           width=800,
                           height=g_height,
                           paper_bgcolor=light_color,
                           plot_bgcolor=light_color,
                           hovermode='closest'
                           )

        fig = go.Figure(data=data, layout=layout)

        plot(fig, filename='%s.html' % _filename.replace(".", "-"), auto_open=False, image_filename=_filename)
