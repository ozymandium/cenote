import matplotlib.pyplot as plt

from cenote import gas_usage as gu
from cenote import config


def plot_gas_usage(plan: gu.Plan, result: gu.Result):

    time = plan.times()
    depth = plan.depths()

    fig, ax = plt.subplots()

    ax.plot(time, depth)
    ax.grid(alpha=0.3)
    ax.set_xlabel("Time ({})".format(str(config.TIME_UNIT)))
    ax.set_ylabel("Depth ({})".format(str(config.DEPTH_UNIT)))
    ax.invert_yaxis()


def plot(plan: gu.Plan, result: gu.Result):
    plot_gas_usage(plan, result)
    plt.show()
