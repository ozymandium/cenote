import matplotlib.pyplot as plt
import numpy as np

from cenote import gas_usage as gu
from cenote import config


TIME_INCREMENT = 0.1  # minute


class Synchronizer:
    def __init__(self):
        self.callbacks = []

    def register(self, callback):
        self.callbacks.append(callback)

    def time_update(self, time):
        for callback in self.callbacks:
            callback(time)


class ProfilePlot:
    def __init__(self, plan: gu.Plan, result: gu.Result, sync: Synchronizer):
        # internal state
        self.times = plan.times()
        self.depths = plan.depths()
        self.time = 0

        # generate plot entities
        self.fig, self.ax = plt.subplots()
        self.x_cursor = self.ax.plot(
            [np.min(self.times), np.min(self.times)],
            [np.min(self.depths), np.max(self.depths)],
            "m",
            alpha=0.5,
        )[0]
        self.y_cursor = self.ax.plot(
            [np.min(self.times), np.max(self.times)],
            [np.min(self.depths), np.min(self.depths)],
            "m",
            alpha=0.5,
        )[0]
        self.ax.plot(self.times, self.depths, "g")
        self.text = self.ax.text(
            0.95,
            0.05,
            "Time: 00:00\nDepth: {} ft".format(self.depths[0]),
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="bottom",
            horizontalalignment="right",
            fontname="monospace",
        )

        # plot accoutrements
        self.ax.set_title("Depth Profile", fontname="monospace")
        self.ax.grid(alpha=0.2)
        self.ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)), fontname="monospace")
        self.ax.set_ylabel("Depth ({})".format(str(config.DEPTH_UNIT)), fontname="monospace")
        self.ax.invert_yaxis()

        # callback setup
        self.fig.canvas.mpl_connect("button_press_event", self.mouse_handler)
        self.fig.canvas.mpl_connect("key_press_event", self.key_handler)

        # synchronizer setup
        self.sync = sync
        self.sync.register(self.time_update_callback)

    def mouse_handler(self, event):
        if event.xdata is None:
            return
        time = np.round(event.xdata, 1)  # 6 second increments
        self.sync.time_update(time)

    def key_handler(self, event):
        if event.key == "right":
            increment = TIME_INCREMENT
        elif event.key == "left":
            increment = -1 * TIME_INCREMENT
        else:
            return
        next_time = np.clip(self.time + increment, np.min(self.times), np.max(self.times))
        self.sync.time_update(next_time)

    def time_update_callback(self, time):
        self.time = time
        depth = np.interp(time, self.times, self.depths)

        # x_cursor
        self.x_cursor.set_xdata([self.time, self.time])
        self.ax.draw_artist(self.x_cursor)

        # y_cursor
        self.y_cursor.set_ydata([depth, depth])
        self.ax.draw_artist(self.y_cursor)

        # text box
        minutes = int(np.floor(self.time))
        seconds = int(np.round((self.time - minutes) * 60))
        self.text.set_text("Time: {min}:{sec:02}\nDepth: {depth} ft".format(min=minutes, sec=seconds, depth=int(depth)))
        # self.ax.draw_artist(self.text)

        # update
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
    plt.style.use("dark_background")

    sync = Synchronizer()
    profile = ProfilePlot(plan, result, sync)
    # plot_gas_usage(plan, result)
    plt.show()
