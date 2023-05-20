import pandas as pd
import numpy as np
import bokeh.plotting

import cenote
import bungee


COLORS = {
    "yellow": "#e6db74",  # string; agreed
    "blue": "#66d9ef",  # builtin / storage type; agreed
    "pink": "#f92672",  # tag name; agreed
    "purple": "#ae81ff",  # constant; agreed
    "brown": "#75715e",  # comments; agreed
    "orange": "#fd971f",  # tag; agreed
    "light-orange": "#ffd569",  # ?
    "green": "#a6e22e",  # function arg; agreed
    "sea-green": "#529b2f",  # ?
    "dark-gray": "#272822",  # background; agreed
    "mid-gray": "#49483e",  # axis lines, ticks, grid; disputed
    "lighter-gray": "#888888",  # label text; disputed
    "lightest-gray": "#cccccc",  # title text; disputed
    "white": "#f8f8f2",  # basic text; disputed
}
COLOR_ORDER = [
    # "green",
    "blue",
    # "pink",
    "yellow",
    "purple",
    "orange",
]


def get_plan_df(output_plan: bungee.Plan) -> str:
    data = []
    for point in output_plan.profile():
        depth = (point.depth.value() * cenote.DEPTH_UNIT).to(cenote.DEPTH_DISPLAY_UNIT)
        time = (point.time.value() * cenote.TIME_UNIT).to(cenote.TIME_DISPLAY_UNIT)
        data.append(["{:~.0f}".format(time), "{:~.0f}".format(depth), point.tank])
    return pd.DataFrame(data, columns=["Time", "Depth", "Tank"])


def get_depth_fig(result: cenote.Result) -> str:
    fig = bokeh.plotting.figure(title="Profile")

    # profile
    fig.line(
        result.time.magnitude, result.depth.magnitude, color=COLORS["green"], legend_label="Profile"
    )
    # ceiling
    idxs = np.nonzero(result.deco.ceiling > 0)[0]
    fig.line(
        result.time[idxs].magnitude,
        result.deco.ceiling[idxs].magnitude,
        color=COLORS["pink"],
        legend_label="Ceiling",
    )
    # compartment ceilings
    for i in range(result.deco.ceilings.shape[0]):
        idxs = np.nonzero(result.deco.ceilings[i, :] > 0)[0]
        if len(idxs):
            x = result.time[idxs].magnitude
            y = result.deco.ceilings[i, idxs].magnitude
            # fig.line(
            #     x,
            #     y,
            #     color=COLORS["pink"],
            #     line_alpha=0.2,
            # )
            fig.varea(x=x, y1=0, y2=y, alpha=0.1, color=COLORS["pink"])

    # formatting
    fig.y_range.flipped = True
    fig.legend.location = "bottom_right"

    return fig


def get_pressure_fig(result: cenote.Result) -> str:
    # make sure there are not more tanks than distinct colors
    if len(result.tank_pressure) > len(COLOR_ORDER):
        raise Exception("Too many tanks to plot pressure in distinct colors")

    fig = bokeh.plotting.figure(title="Tank Pressure")

    for idx, tank in enumerate(result.tank_pressure):
        color = COLORS[COLOR_ORDER[idx]]
        fig.line(
            result.time.magnitude,
            result.tank_pressure[tank].magnitude,
            color=color,
            legend_label=tank,
        )

    return fig


def get_gradient_fig(result: cenote.Result) -> str:
    fig = bokeh.plotting.figure(title="Gradient")

    # gradient of controlling compartment
    idxs = np.nonzero(result.deco.gradient >= 0)[0]
    fig.line(result.time[idxs].magnitude, result.deco.gradient[idxs] * 100, color=COLORS["green"])
    # gradient of each compartment
    for i in range(result.deco.gradients.shape[0]):
        idxs = np.nonzero(result.deco.gradients[i, :] > 0)[0]
        if len(idxs):
            fig.line(
                result.time[idxs].magnitude,
                result.deco.gradients[i, idxs] * 100,
                color=COLORS["green"],
                line_alpha=0.3,
            )

    # formatting
    # plt.ylabel("Gradient (%)")

    return fig


# def get_compartment_fig(result: cenote.Result) -> str:
#     # single compartment analysis
#     # FIXME: add dropdown to configure which compartment is displayed

#     COMPARTMENT = 5

#     fig, axes = plt.subplots(1, 2)

#     axes[0].plot(result.ambient_pressure, result.ambient_pressure, "b", label="Ambient")
#     axes[0].plot(
#         result.deco.M0s[COMPARTMENT, :],
#         result.deco.tissue_pressures[COMPARTMENT, :],
#         "r",
#         label="M value",
#     )
#     axes[0].plot(
#         result.ambient_pressure, result.deco.tissue_pressures[COMPARTMENT, :], "g", label="Tissue"
#     )
#     axes[0].legend(loc="best")
#     axes[0].axis("equal")
#     axes[0].grid(alpha=0.2)
#     axes[0].set_title("Compartment vs Ambient Pressure")

#     axes[1].plot(result.time, result.ambient_pressure, "b", label="Ambient")
#     axes[1].plot(result.time, result.deco.M0s[COMPARTMENT, :], "r", label="M value")
#     axes[1].plot(result.time, result.deco.tissue_pressures[COMPARTMENT, :], "g", label="Tissue")
#     axes[1].legend(loc="best")
#     axes[1].grid(alpha=0.2)
#     axes[1].invert_yaxis()
#     axes[1].set_title("Compartment Pressure vs Time")

#     return fig_to_html(fig)
