import matplotlib.pyplot as plt
import numpy as np

from cenote import gas_usage as gu
from cenote import config


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
            increment = config.TIME_INCREMENT.magnitude
        elif event.key == "left":
            increment = -1 * config.TIME_INCREMENT.magnitude
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


class UsagePlot:
    def __init__(self, plan: gu.Plan, result: gu.Result, sync: Synchronizer):
        # internal state
        self.times = result.times()
        self.usages = result.usages()
        self.time = 0

        # generate plot entities
        self.fig, self.ax = plt.subplots()
        self.x_cursor = self.ax.plot(
            [np.min(self.times), np.min(self.times)],
            [0, np.max([np.max(u) for u in self.usages.values()])],
            "m",
            alpha=0.5,
        )[0]
        for name in self.usages:
            self.ax.plot(self.times, self.usages[name], label=name)
        self.text = self.ax.text(
            0.05,
            0.95,
            "Time: 00:00\n"
            + "\n".join(
                [
                    "{name}: {usage} cuft".format(name=name, usage=self.usages[name][0])
                    for name in self.usages
                ]
            ),
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            horizontalalignment="left",
            fontname="monospace",
        )

        # plot accoutrements
        self.fig.canvas.set_window_title("Gas Usage")
        self.ax.set_title("Gas Usage", fontname="monospace")
        self.ax.grid(alpha=0.2)
        self.ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)), fontname="monospace")
        self.ax.set_ylabel("Gas Usage (cuft)", fontname="monospace")

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
            increment = config.TIME_INCREMENT.magnitude
        elif event.key == "left":
            increment = -1 * config.TIME_INCREMENT.magnitude
        else:
            return
        next_time = np.clip(self.time + increment, np.min(self.times), np.max(self.times))
        self.sync.time_update(next_time)

    def time_update_callback(self, time):
        self.time = time
        usage = {name: np.interp(time, self.times, self.usages[name]) for name in self.usages}

        # x_cursor
        self.x_cursor.set_xdata([self.time, self.time])

        # text box
        minutes = int(np.floor(self.time))
        seconds = int(np.round((self.time - minutes) * 60))
        if seconds == 60:
            minutes += 1
            seconds = 0
        self.text.set_text(
            "Time: {min}:{sec:02}\n".format(min=minutes, sec=seconds)
            + "\n".join(
                [
                    "{name}: {usage} cuft".format(name=name, usage=int(usage[name]))
                    for name in self.usages
                ]
            )
        )

        # update
        self.fig.canvas.draw()
        self.fig.canvas.blit(self.ax.bbox)


class PressurePlot:
    def __init__(self, plan: gu.Plan, result: gu.Result, sync: Synchronizer):
        # internal state
        self.times = result.times()
        self.pressures = result.pressures()
        self.time = 0

        # generate plot entities
        self.fig, self.ax = plt.subplots()
        self.x_cursor = self.ax.plot(
            [np.min(self.times), np.min(self.times)],
            [0, np.max([np.max(u) for u in self.pressures.values()])],
            "m",
            alpha=0.5,
        )[0]
        for name in self.pressures:
            self.ax.plot(self.times, self.pressures[name], label=name)
        self.text = self.ax.text(
            0.05,
            0.05,
            "Time: 00:00\n"
            + "\n".join(
                [
                    "{name}: {pressure} psi".format(
                        name=name, pressure=int(self.pressures[name][0])
                    )
                    for name in self.pressures
                ]
            ),
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="bottom",
            horizontalalignment="left",
            fontname="monospace",
        )

        # plot accoutrements
        self.fig.canvas.set_window_title("Pressure")
        self.ax.set_title("Pressure", fontname="monospace")
        self.ax.grid(alpha=0.2)
        self.ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)), fontname="monospace")
        self.ax.set_ylabel("Pressure (psi)", fontname="monospace")

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
            increment = config.TIME_INCREMENT.magnitude
        elif event.key == "left":
            increment = -1 * config.TIME_INCREMENT.magnitude
        else:
            return
        next_time = np.clip(self.time + increment, np.min(self.times), np.max(self.times))
        self.sync.time_update(next_time)

    def time_update_callback(self, time):
        self.time = time
        pressure = {
            name: np.interp(time, self.times, self.pressures[name]) for name in self.pressures
        }

        # x_cursor
        self.x_cursor.set_xdata([self.time, self.time])

        # text box
        minutes = int(np.floor(self.time))
        seconds = int(np.round((self.time - minutes) * 60))
        if seconds == 60:
            minutes += 1
            seconds = 0
        self.text.set_text(
            "Time: {min}:{sec:02}\n".format(min=minutes, sec=seconds)
            + "\n".join(
                [
                    "{name}: {pressure} psi".format(name=name, pressure=int(pressure[name]))
                    for name in self.pressures
                ]
            )
        )

        # update
        self.fig.canvas.draw()
        self.fig.canvas.blit(self.ax.bbox)


def plot(plan: gu.Plan, result: gu.Result):
    plt.style.use("dark_background")

    sync = Synchronizer()
    profile = ProfilePlot(plan, result, sync)
    usage = UsagePlot(plan, result, sync)
    pressure = PressurePlot(plan, result, sync)
    plt.show()
