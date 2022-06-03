import matplotlib.pyplot as plt
import numpy as np

from cenote import gas_usage as gu
from cenote import config


# class Synchronizer:

#     def __init__(self):

class ProfilePlot:

    def __init__(self, plan: gu.Plan, result: gu.Result):

        self.fig, self.ax = plt.subplots()

        self.time = plan.times()
        self.depth = plan.depths()

        self.cursor = self.ax.plot([0, 0], [np.min(self.depth), np.max(self.depth)], "m", alpha=0.7)[0]

        self.ax.plot(self.time, self.depth, "g")
        
        self.ax.set_title("Depth Profile")
        self.ax.grid(alpha=0.3)
        self.ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)))
        self.ax.set_ylabel("Depth ({})".format(str(config.DEPTH_UNIT)))
        self.ax.invert_yaxis()

        self.fig.canvas.mpl_connect('button_press_event', self.mouse_handler)

    def mouse_handler(self, event):
        if event.xdata is None:
            return
        self.update_cursor(event.xdata)

    def update_cursor(self, time):
        self.cursor.set_xdata([event.xdata, event.xdata])
        self.ax.draw_artist(self.cursor)
        self.fig.canvas.draw()
        self.fig.canvas.blit(self.ax.bbox)


    # def key_handler(event)




# def plot_gas_usage(plan: gu.Plan, result: gu.Result):
#     time = plan.times()
#     depth = plan.depths()

#     fig, ax = plt.subplots()

#     ax.plot(time, depth)
#     ax.grid(alpha=0.3)
#     ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)))
#     ax.set_ylabel("Gas Usage ({})".format(str(config.VOLUME_UNIT)))


def plot(plan: gu.Plan, result: gu.Result):
    plt.style.use('dark_background')
    profile = ProfilePlot(plan, result)
    # plot_gas_usage(plan, result)
    plt.show()
