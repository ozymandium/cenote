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
        self.fig.canvas.set_window_title("Depth Profile")
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

        # y_cursor
        self.y_cursor.set_ydata([depth, depth])

        # text box
        minutes = int(np.floor(self.time))
        seconds = int(np.round((self.time - minutes) * 60))
        if seconds == 60:
            minutes += 1
            seconds = 0
        self.text.set_text(
            "Time: {min}:{sec:02}\nDepth: {depth} ft".format(
                min=minutes, sec=seconds, depth=int(depth)
            )
        )

        # update
        self.fig.canvas.draw()
        self.fig.canvas.blit(self.ax.bbox)


class ConsumptionPlot:
    def __init__(self, plan: gu.Plan, result: gu.Result, sync: Synchronizer):
        # internal state
        self.times = plan.times()
        self.consumptions = result.consumed_volumes()
        self.time = 0

        # generate plot entities
        self.fig, self.ax = plt.subplots()
        self.x_cursor = self.ax.plot(
            [np.min(self.times), np.min(self.times)],
            [np.min(self.consumptions), np.max(self.consumptions)],
            "m",
            alpha=0.5,
        )[0]
        self.y_cursor = self.ax.plot(
            [np.min(self.times), np.max(self.times)],
            [np.min(self.consumptions), np.min(self.consumptions)],
            "m",
            alpha=0.5,
        )[0]
        self.ax.plot(self.times, self.consumptions, "g")
        self.text = self.ax.text(
            0.95,
            0.05,
            "Time: 00:00\nUsed: {} cuft".format(self.consumptions[0]),
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="bottom",
            horizontalalignment="right",
            fontname="monospace",
        )

        # plot accoutrements
        self.fig.canvas.set_window_title("Gas Consumption")
        self.ax.set_title(
            "Gas Consumption\n({})".format(str(config.VOLUME_UNIT)), fontname="monospace"
        )
        self.ax.grid(alpha=0.2)
        self.ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)), fontname="monospace")
        self.ax.set_ylabel("Tank ___", fontname="monospace")

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
        consumption = np.interp(time, self.times, self.consumptions)

        # x_cursor
        self.x_cursor.set_xdata([self.time, self.time])

        # y_cursor
        self.y_cursor.set_ydata([consumption, consumption])

        # text box
        minutes = int(np.floor(self.time))
        seconds = int(np.round((self.time - minutes) * 60))
        if seconds == 60:
            minutes += 1
            seconds = 0
        self.text.set_text(
            "Time: {min}:{sec:02}\nUsed: {consumption} cuft".format(
                min=minutes, sec=seconds, consumption=int(consumption)
            )
        )

        # update
        self.fig.canvas.draw()
        self.fig.canvas.blit(self.ax.bbox)


def plot(plan: gu.Plan, result: gu.Result):
    plt.style.use("dark_background")

    sync = Synchronizer()
    profile = ProfilePlot(plan, result, sync)
    consumption = ConsumptionPlot(plan, result, sync)
    plt.show()
