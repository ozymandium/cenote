import matplotlib.pyplot as plt

from cenote import gas_usage as gu
from cenote import config


class ProfilePlot:

    def __init__(self, plan: gu.Plan, result: gu.Result):

        self.fig, self.ax = plt.subplots()

        self.time = plan.times()
        self.depth = plan.depths()

        self.ax.plot(self.time, self.depth, "g")
        self.ax.grid(alpha=0.3)
        self.ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)))
        self.ax.set_ylabel("Depth ({})".format(str(config.DEPTH_UNIT)))
        self.ax.invert_yaxis()


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
