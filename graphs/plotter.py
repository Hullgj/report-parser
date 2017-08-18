"""Here we are plotting a graph of its calls to APIs for each binary. We also process the calls to APIs per category,
as defined in the randep model, and plot their start and end times. This gives a graphical representation of how the
sample behaves according to the model.
Since the data has been processed by the report parser, we need to read the start and end time of each API per binary.
The axis are trace_start: x = start_times, y = apis; trace_end: x = end_times, y = apis;
Perhaps we could group the APIs into categories by using colour of the keys in the legend of the graph"""

from plotly.offline import plot
import plotly.graph_objs as go

class Plot(object):
    def __init__(self):
        pass

    def plots(self, _filename, apis, start_times, end_times):
        """Each binary has a filename, list of APIs, and each API has start and end times. These parameters are
        fed into this function to make two traces for start and end, where the x-axis is the list of times, and
        y-axis is the list of APIs"""

        trace0 = go.Scatter(
            x = start_times,
            y = apis,
            marker = dict(color = 'rgba(156, 165, 196, 0.95)',
                          line = dict(width = 1,
                                      color = 'rgba(156, 165, 196, 1.0)'),
                          size = 12),
            mode = "markers",
            name = "Start Time"
        )
        trace1 = go.Scatter(
            x = end_times,
            y = apis,
            marker = dict(color = 'rgba(204, 204, 204, 0.95)',
                          line = dict(width = 1,
                                      color = 'rgba(217, 217, 217, 1.0)'),
                          size = 12),
            mode = "markers",
            name = "End Time"
        )


        data = [trace0, trace1]
        layout = go.Layout(title = "%s's API Start and End Times" % _filename,
                           xaxis = dict(title = "Time (s)",
                               showgrid = False,
                               showline = True,
                               linecolor='rgb(102, 102, 102)',
                               titlefont=dict(color='rgb(204, 204, 204)'),
                               tickfont=dict(color='rgb(102, 102, 102)'),
                               autotick=False,
                               dtick=10,
                               ticks='outside',
                               tickcolor='rgb(102, 102, 102)'),
                           margin=dict(
                               l=140,
                               r=40,
                               b=50,
                               t=80
                           ),
                           legend=dict(
                               font=dict(
                                   size=10,
                               ),
                               yanchor='middle',
                               xanchor='right',
                           ),
                           width=800,
                           height=600,
                           paper_bgcolor='rgb(254, 247, 234)',
                           plot_bgcolor='rgb(254, 247, 234)',
                           hovermode='closest'
        )

        fig = go.Figure(data=data, layout=layout)

        plot(fig, filename='%s.html' % _filename)