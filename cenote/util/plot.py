from cenote.usage import Plan, Result
from cenote import config
from cenote import parse

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import argparse
import os
import yaml
import sys


UREG = config.UREG


class Synchronizer:
    def __init__(self):
        self.callbacks = []

    def register(self, callback):
        self.callbacks.append(callback)

    def time_update(self, time):
        for callback in self.callbacks:
            callback(time)


class ProfilePlot:
    def __init__(self, plan: Plan, result: Result, sync: Synchronizer):
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
    def __init__(self, plan: Plan, result: Result, sync: Synchronizer):
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
            0.7,
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
        self.ax.legend(loc="best")

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
    def __init__(self, plan: Plan, result: Result, sync: Synchronizer):
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
        self.ax.legend(loc="best")

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


class PO2Plot:
    def __init__(self, plan: Plan, result: Result, sync: Synchronizer):
        # internal state
        self.times = result.times()
        self.po2s = result.po2s()
        self.time = 0

        # generate plot entities
        self.fig, self.ax = plt.subplots()
        self.x_cursor = self.ax.plot(
            [np.min(self.times), np.min(self.times)],
            [np.min(self.po2s), np.max(self.po2s)],
            "m",
            alpha=0.5,
        )[0]
        self.y_cursor = self.ax.plot(
            [np.min(self.times), np.max(self.times)],
            [np.min(self.po2s), np.min(self.po2s)],
            "m",
            alpha=0.5,
        )[0]
        # self.ax.plot(self.times, self.po2s, "g")
        self.text = self.ax.text(
            0.95,
            0.05,
            "Time: 00:00\nPO2: {:.2f} ata".format(self.po2s[0]),
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="bottom",
            horizontalalignment="right",
            fontname="monospace",
        )

        # stuff to make a colormap for the value of po2
        # https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/multicolored_line.html
        # Create a set of line segments so that we can color them individually
        # This creates the points as a N x 1 x 2 array so that we can stack points
        # together easily to get the segments. The segments array for line collection
        # needs to be (numlines) x (points per line) x 2 (for x and y)
        points = np.array([self.times, self.po2s]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        mean_po2s = (self.po2s[1:] + self.po2s[:-1]) * 0.5
        # Create a continuous norm to map from data points to colors
        norm = plt.Normalize(0.18, 1.6)
        lc = LineCollection(segments, cmap="RdYlGn_r", norm=norm)
        # Set the values used for colormapping
        lc.set_array(mean_po2s)
        lc.set_linewidth(2)
        line = self.ax.add_collection(lc)
        self.fig.colorbar(line, ax=self.ax)

        # plot accoutrements
        self.fig.canvas.set_window_title("Partial Pressure")
        self.ax.set_title("Partial Pressure", fontname="monospace")
        self.ax.grid(alpha=0.2)
        self.ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)), fontname="monospace")
        self.ax.set_ylabel("PO2 (ata)", fontname="monospace")

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
        po2 = np.interp(time, self.times, self.po2s)

        # x_cursor
        self.x_cursor.set_xdata([self.time, self.time])

        # y_cursor
        self.y_cursor.set_ydata([po2, po2])

        # text box
        minutes = int(np.floor(self.time))
        seconds = int(np.round((self.time - minutes) * 60))
        if seconds == 60:
            minutes += 1
            seconds = 0
        self.text.set_text(
            "Time: {min}:{sec:02}\nPO2: {po2:.2f} ata".format(
                min=minutes, sec=seconds, po2=po2
            )
        )

        # update
        self.fig.canvas.draw()
        self.fig.canvas.blit(self.ax.bbox)


def plot(plan: Plan, result: Result):
    plt.style.use("dark_background")

    sync = Synchronizer()
    profile = ProfilePlot(plan, result, sync)
    usage = UsagePlot(plan, result, sync)
    pressure = PressurePlot(plan, result, sync)
    po2 = PO2Plot(plan, result, sync)
    plt.show()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("yaml_path", help="Path to YAML file containing dive plan.")
    return parser.parse_args()


def main():
    args = parse_args()

    plan = parse.plan_from_yaml(args.yaml_path)
    result = Result(plan)

    plot(plan, result)
