from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Legend, LegendItem, Label
from lightweight_charts import Chart, JupyterChart

def plot(self,df: pd.DataFrame) -> None:
    # Create a ColumnDataSource from the DataFrame
    source = ColumnDataSource(df)
    # Create a figure
    p = figure(title=f"{self.symbol} Bar", x_axis_label="minute", y_axis_label="close price")
    # Add a line glyph
    p.line(x="time", y="c", source=source)
    # Format x-axis labels for EST
    p.xaxis.formatter = DatetimeTickFormatter(
                        hours="%H:%M",
                        minutes="%H:%M")

    # Show the plot
    show(p)


def tvplot(self,df: pd.DataFrame):
    # d = df[['c','o','h','l','t','v']]
    df = df.rename(columns={'c': 'close',
                        'o': 'open',
                        'h': 'high',
                        'l': 'low',
                        't': 'time',
                        'v': 'volume'  }, inplace=True)
    # chart = Chart()
    c = JupyterChart(width=600,height=400)
    c.set(df)
    c.load()