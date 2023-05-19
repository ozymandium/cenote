#!/usr/bin/env python3
import sys
import os
import bungee
import cenote
import yaml
import pint
import numpy as np
import mpld3
import matplotlib.pyplot as plt
import http.server
import flask
import pretty_html_table
import pandas as pd
import flask_wtf
import flask_codemirror
import flask_codemirror.fields
import wtforms
import traceback


def get_result(input_text: str) -> cenote.Result:
    input_plan = cenote.get_plan(input_text, is_path=False)
    output_plan = bungee.replan(input_plan)
    result = cenote.get_result(output_plan)
    return output_plan, result


def get_plan_table_html(output_plan: bungee.Plan) -> str:
    data = []
    for point in output_plan.profile():
        depth = (point.depth.value() * cenote.DEPTH_UNIT).to(cenote.DEPTH_DISPLAY_UNIT)
        time = (point.time.value() * cenote.TIME_UNIT).to(cenote.TIME_DISPLAY_UNIT)
        data.append(["{:~.0f}".format(time), "{:~.0f}".format(depth), point.tank])
    return pretty_html_table.build_table(
        pd.DataFrame(data, columns=["Time", "Depth", "Tank"]), "green_dark"
    )


def get_depth_plot_html(result: cenote.Result) -> str:
    fig = plt.figure()
    plt.plot(result.time, result.depth, "g", label="Profile")
    idxs = np.nonzero(result.deco.ceiling > 0)[0]
    plt.plot(result.time[idxs], result.deco.ceiling[idxs], "r", label="Ceiling")
    plt.legend(loc="best")
    for i in range(result.deco.ceilings.shape[0]):
        idxs = np.nonzero(result.deco.ceilings[i, :] > 0)[0]
        if len(idxs):
            plt.plot(result.time[idxs], result.deco.ceilings[i, idxs], "r", alpha=0.2)
    plt.gca().invert_yaxis()
    plt.grid(alpha=0.2)
    plt.title("Profile")
    return mpld3.fig_to_html(fig)


def get_pressure_plot_html(result: cenote.Result) -> str:
    fig = plt.figure()
    for tank in result.tank_pressure:
        plt.plot(result.time, result.tank_pressure[tank], label=tank)
    plt.grid(alpha=0.2)
    plt.title("Tank Pressure")
    plt.legend(loc="best")
    return mpld3.fig_to_html(fig)


def get_gradient_plot_html(result: cenote.Result) -> str:
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
    return mpld3.fig_to_html(fig)


def get_compartment_plot_html(result: cenote.Result) -> str:
    # single compartment analysis
    # FIXME: add dropdown to configure which compartment is displayed

    COMPARTMENT = 5

    # ambient_pressure = [cenote.pressure_from_depth(d, plan.water()) for d in result.depth]
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

    return mpld3.fig_to_html(fig)


SECRET_KEY = "secret!"
# mandatory
CODEMIRROR_LANGUAGES = ["yaml"]
# optional
CODEMIRROR_THEME = "3024-day"
CODEMIRROR_ADDONS = (("display", "placeholder"),)


app = flask.Flask(__name__)


class Form(flask_wtf.FlaskForm):
    input_text = flask_codemirror.fields.CodeMirrorField(
        language="yaml", config={"lineNumbers": "true"},
    )
    open_button = wtforms.fields.SubmitField(label="Open")
    plan_button = wtforms.fields.SubmitField(label="Plan")
    save_button = wtforms.fields.SubmitField(label="Save")


@app.route("/", methods=["GET", "POST"])
def index():
    form = Form()
    
    input_text = form.input_text.data
    open_clicked = form.open_button.data
    plan_clicked = form.plan_button.data
    save_clicked = form.save_button.data

    kwargs = {}
    kwargs["form"] = form

    if input_text is None or len(input_text) == 0:
        return flask.render_template("index.html", **kwargs)
    
    if plan_clicked:
        try:
            output_plan, result = get_result(input_text)
        except Exception as exc:
            flask.flash("There's a problem with your dive plan:\n{}".format(traceback.format_exc()))
            return flask.render_template("index.html", **kwargs)
        
        kwargs["plan_table"] = get_plan_table_html(output_plan)
        kwargs["depth_plot"] = get_depth_plot_html(result)
        kwargs["pressure_plot"] = get_pressure_plot_html(result)
        kwargs["gradient_plot"] = get_gradient_plot_html(result)
        kwargs["compartment_plot"] = get_compartment_plot_html(result)

        return flask.render_template("index.html", **kwargs)

    elif open_clicked:
        return flask.render_template("index.html", **kwargs)
    elif save_clicked:
        return flask.render_template("index.html", **kwargs)
    else:
        flask.flash("unknown")
        return flask.render_template("index.html", **kwargs)


# pick up config variables
app.config.from_object(__name__)
codemirror = flask_codemirror.CodeMirror(app)


if __name__ == "__main__":
    cenote.UREG.setup_matplotlib()
    app.run(host="0.0.0.0", port=8888, debug=True, use_reloader=True)
