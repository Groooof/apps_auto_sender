import datetime
from tkinter import *
from tkinter.ttk import *
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from time import sleep
import psutil
import speedtest
from src.GUI.styles import Colors

matplotlib.use("TkAgg")
sp = speedtest.Speedtest()


class MyPlot:
    def __init__(self, ax, line_pos=0, time_interval=20, y_ticks=(), color='black', y_label='', legend=False):
        self.colors = Colors()
        self.ax = ax
        self.time_interval = time_interval
        self.y_ticks = y_ticks
        self.color = color
        self.x_values = [int(datetime.datetime.now().timestamp())]
        self.y_values = [0]
        self.y_label = y_label
        self.line_pos = line_pos
        self.legend = legend

        self.ax.set_facecolor(self.colors.main_lighter)
        self.ax.spines['top'].set_visible(False)
        self.redraw()

    def set_settings(self):
        self.ax.set_ylabel(self.y_label, labelpad=0, fontsize='large')
        self.ax.bar(label='Inet Speed', x=0.5, height=0.1, color='red')
        self.ax.bar(label='CPU', x=0.5, height=100, color='blue')
        self.ax.axhline(y=self.line_pos, xmin=0.0, xmax=1.0, color=self.color, linewidth=0.5)
        if self.legend:
            self.ax.legend()

        self.ax.autoscale(axis='y', enable=False)
        self.ax.set_yticks(self.y_ticks)

    def redraw(self):
        self.ax.clear()
        self.set_settings()
        x_matplotlib_dates = tuple([timestamp_to_matplotlib(i) for i in self.x_values])

        self.ax.set_xlim((x_matplotlib_dates[0],
                          timestamp_to_matplotlib(self.x_values[0] + self.time_interval * 60)))

        self.ax.plot_date(x_matplotlib_dates, self.y_values,
                          color=self.color, label=self.y_label, linestyle='-', marker=',', linewidth=1)

    def twinx(self):
        twin_ax = self.ax.twinx()
        twin_ax.xaxis.label.set_color(self.colors.text)
        twin_ax.spines['bottom'].set_visible(False)
        twin_ax.spines['left'].set_visible(False)
        twin_ax.set_frame_on(False)
        return twin_ax

    def append_to_end(self, x, y):
        self.x_values.append(x)
        self.y_values.append(y)

    def delete_first(self):
        self.x_values.pop(0)
        self.y_values.pop(0)


class Graph(Frame):
    def __init__(self, parent, time_interval):
        super().__init__(parent)
        self.colors = Colors()
        self.time_interval = time_interval

        self.y_ticks_inet = [0, 25, 50, 75, 100]
        self.y_ticks_cpu = [0, 25, 50, 75, 100]
        self.inet_critical = 20
        self.cpu_critical = 70

        self.figure = Figure(figsize=(5, 2), dpi=65, facecolor=self.colors.main_lighter)

        ax_inet = self.figure.add_axes((0.05, 0.15, 0.91, 0.85), label='inet')
        self.inet_plot = MyPlot(ax_inet, y_ticks=self.y_ticks_inet, color='red', time_interval=self.time_interval,
                                y_label='Inet Speed, Mb/s', line_pos=self.inet_critical, legend=True)

        ax_cpu = self.inet_plot.twinx()
        self.cpu_plot = MyPlot(ax_cpu, y_ticks=self.y_ticks_cpu, color='blue', time_interval=self.time_interval,
                               y_label='CPU, %', line_pos=self.cpu_critical)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def update_plot(self, plot, value):
        curr_time = int(datetime.datetime.now().timestamp())

        plot.append_to_end(curr_time, value)
        if len(plot.x_values) > 200:
            plot.delete_first()

        plot.redraw()

    def update_graph(self):
        #print('Получаем данные для графиков')
        try:
            cpu_percent = psutil.cpu_percent()
            inet_speed = (sp.download() / 1024) / 1024
        except Exception as ex:
            return
        #print(f'Inet speed: {inet_speed} Mb/s\nCPU load: {cpu_percent} %')

        self.update_plot(self.inet_plot, inet_speed)
        self.update_plot(self.cpu_plot, cpu_percent)
        self.canvas.draw()

    def start(self):
        while True:
            sleep(2)
            self.update_graph()


def get_time_h_m(self, time):
        normalize_nulls = lambda num: str(num) if len(str(num)) != 1 else '0' + str(num)
        full_date = datetime.datetime.fromtimestamp(time)
        return normalize_nulls(full_date.hour) + ':' + normalize_nulls(full_date.minute)


def matplotlib_to_timestamp(self, matplotlib_date):
        return datetime.datetime.timestamp(matplotlib.dates.num2date(matplotlib_date))


def timestamp_to_matplotlib(timestamp):
        return matplotlib.dates.date2num(datetime.datetime.fromtimestamp(timestamp))
