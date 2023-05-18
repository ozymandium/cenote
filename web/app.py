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
import argparse
import flask
import pretty_html_table
import pandas as pd

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default=os.path.join(os.environ["SRC_DIR"], "examples", "big.yaml"), help="Path to YAML config")
    parser.add_argument("-p", "--port", type=int, default=8000)
    return parser.parse_args()


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
        # print("{depth:~.0f}\t{time:~.0f}\t{tank}".format(depth=depth, time=time, tank=point.tank))
        data.append(
            [
                "{:~.0f}".format(depth),
                "{:~.0f}".format(time),
                point.tank
            ]
        )
    return pretty_html_table.build_table(pd.DataFrame(data, columns=["Depth", "Time", "Tank"]), "green_dark")


def get_depth_plot_html(result: cenote.Result) -> str:
    depth_fig = plt.figure()
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
    depth_html = mpld3.fig_to_html(depth_fig)
    return depth_html


app = flask.Flask(__name__)


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    input_text = flask.request.form["input_text"]
    output_plan, result = get_result(input_text)
    plan_table_html = get_plan_table_html(output_plan)


    return flask.render_template("index.html", plan_table=plan_table_html)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True, use_reloader=True)
