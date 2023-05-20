import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import bokeh.plotting

import cenote
import bungee


def get_plan_df(output_plan: bungee.Plan) -> str:
    data = []
    for point in output_plan.profile():
        depth = (point.depth.value() * cenote.DEPTH_UNIT).to(cenote.DEPTH_DISPLAY_UNIT)
        time = (point.time.value() * cenote.TIME_UNIT).to(cenote.TIME_DISPLAY_UNIT)
        data.append(["{:~.0f}".format(time), "{:~.0f}".format(depth), point.tank])
    return pd.DataFrame(data, columns=["Time", "Depth", "Tank"])


def get_depth_fig(result: cenote.Result) -> str:
    # fig = plt.figure()
    # plt.plot(result.time, result.depth, "g", label="Profile")
    # idxs = np.nonzero(result.deco.ceiling > 0)[0]
    # plt.plot(result.time[idxs], result.deco.ceiling[idxs], "r", label="Ceiling")
    # plt.legend(loc="best")
    # for i in range(result.deco.ceilings.shape[0]):
    #     idxs = np.nonzero(result.deco.ceilings[i, :] > 0)[0]
    #     if len(idxs):
    #         plt.plot(result.time[idxs], result.deco.ceilings[i, idxs], "r", alpha=0.2)
    # plt.gca().invert_yaxis()
    # plt.grid(alpha=0.2)
    # plt.title("Profile")
    # return fig_to_html(fig)

    fig = bokeh.plotting.figure()
    fig.line(result.time.magnitude, result.depth.magnitude)

    return fig


def get_pressure_fig(result: cenote.Result) -> str:
    # fig = plt.figure()
    # for tank in result.tank_pressure:
    #     plt.plot(result.time, result.tank_pressure[tank], label=tank)
    # plt.grid(alpha=0.2)
    # plt.title("Tank Pressure")
    # plt.legend(loc="best")
    # return fig_to_html(fig)

    fig = bokeh.plotting.figure()
    for tank in result.tank_pressure:
        fig.line(result.time.magnitude, result.tank_pressure[tank].magnitude)
    return fig


def get_gradient_fig(result: cenote.Result) -> str:
    fig = plt.figure()
    idxs = np.nonzero(result.deco.gradient >= 0)[0]
    plt.plot(result.time[idxs], result.deco.gradient[idxs] * 100, "g")
    for i in range(result.deco.gradients.shape[0]):
        idxs = np.nonzero(result.deco.gradients[i, :] > 0)[0]
        if len(idxs):
            plt.plot(result.time[idxs], result.deco.gradients[i, idxs] * 100, "g", alpha=0.3)
    plt.grid(alpha=0.2)
    plt.ylabel("Gradient (%)")
    plt.title("Gradient")
    return fig_to_html(fig)


def get_compartment_fig(result: cenote.Result) -> str:
    # single compartment analysis
    # FIXME: add dropdown to configure which compartment is displayed

    COMPARTMENT = 5

    fig, axes = plt.subplots(1, 2)

    axes[0].plot(result.ambient_pressure, result.ambient_pressure, "b", label="Ambient")
    axes[0].plot(
        result.deco.M0s[COMPARTMENT, :],
        result.deco.tissue_pressures[COMPARTMENT, :],
        "r",
        label="M value",
    )
    axes[0].plot(
        result.ambient_pressure, result.deco.tissue_pressures[COMPARTMENT, :], "g", label="Tissue"
    )
    axes[0].legend(loc="best")
    axes[0].axis("equal")
    axes[0].grid(alpha=0.2)
    axes[0].set_title("Compartment vs Ambient Pressure")

    axes[1].plot(result.time, result.ambient_pressure, "b", label="Ambient")
    axes[1].plot(result.time, result.deco.M0s[COMPARTMENT, :], "r", label="M value")
    axes[1].plot(result.time, result.deco.tissue_pressures[COMPARTMENT, :], "g", label="Tissue")
    axes[1].legend(loc="best")
    axes[1].grid(alpha=0.2)
    axes[1].invert_yaxis()
    axes[1].set_title("Compartment Pressure vs Time")

    return fig_to_html(fig)
