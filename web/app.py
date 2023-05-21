#!/usr/bin/env python3
import sys
import os
import traceback
import json
import base64

import flask
import flask_wtf
import flask_wtf.file
import flask_codemirror
import flask_codemirror.fields
import wtforms
import werkzeug.utils
import bokeh.embed
import bokeh.resources
import bokeh.themes

import pretty_html_table

import plots
import bungee
import cenote


SECRET_KEY = "secret!"
# mandatory
CODEMIRROR_LANGUAGES = [
    "json",
]
# optional
CODEMIRROR_THEME = "monokai"
CODEMIRROR_ADDONS = (("display", "placeholder"),)

# ermagerd what if more than one person uses it?
# lol that'll never happen
USER_PLAN_PATH = "/tmp/user_plan.json"


def minify_json(blob: str) -> str:
    return json.dumps(json.loads(blob), separators=(",", ":"))


def prettify_json(blob: str) -> str:
    return json.dumps(json.loads(blob), indent=4, sort_keys=True)


def base64_from_json(blob: str) -> bytes:
    return base64.b64encode(minify_json(blob).encode("utf-8"))


def json_from_base64(blob: str) -> str:
    return base64.b64decode(blob)


class State:
    """No bungee/cenote data types, only python builtins.

    Stores everything needed to replicate web app state, including the user plan and app config
    """

    def __init__(self, plan: dict):
        self.plan = plan

    @staticmethod
    def from_dict(data: dict):
        return State(data["plan"])

    @staticmethod
    def from_json_str(json_str: str):
        return State.from_dict(json.loads(json_str))

    @staticmethod
    def from_b64_str(b64_str: str):
        return State.from_json_str(json_from_base64(b64_str))

    def to_dict(self) -> dict:
        return {
            "plan": self.plan,
        }

    def to_json_str(self) -> str:
        # FIXME: json dump/parse/dump can be simplified to be faster
        return minify_json(json.dumps(self.to_dict()))

    def to_b64_str(self) -> str:
        return base64_from_json(self.to_json_str())


class PlanUploadForm(flask_wtf.FlaskForm):
    file_picker = flask_wtf.file.FileField(
        validators=[
            flask_wtf.file.FileRequired(),
            flask_wtf.file.FileAllowed(
                [
                    "json",
                ],
                "Only JSON files are supported.",
            ),
        ]
    )
    upload_button = wtforms.fields.SubmitField(label="Upload")


class PlanPlanForm(flask_wtf.FlaskForm):
    plot_button = wtforms.fields.SubmitField(label="Plot")
    save_button = wtforms.fields.SubmitField(label="Save")


app = flask.Flask(__name__)

# def setup_plots() -> None:
#     cenote.UREG.setup_matplotlib(True)
#     cenote.UREG.mpl_formatter = "{:~P}"
#     plt.style.use("dark_background")


@app.route("/plan", methods=["GET", "POST"], defaults={"state_b64": None})
@app.route("/plan/<state_b64>", methods=["GET", "POST"])
def plan(state_b64: str):
    # create forms
    upload_form = PlanUploadForm()
    plan_form = PlanPlanForm()

    # harvest information from forms
    upload_json = upload_form.file_picker.data
    upload_clicked = upload_form.upload_button.data
    plot_clicked = plan_form.plot_button.data
    save_clicked = plan_form.save_button.data

    kwargs = {
        "upload_form": upload_form,
        "plan_form": plan_form,
    }

    if state_b64 is not None:
        state = State.from_b64_str(state_b64)
    else:
        state = None

    if upload_clicked and upload_json is not None:
        # it will be of type FileStorage
        # path = werkzeug.utils.secure_filename(upload_json.filename)
        upload_json.save(USER_PLAN_PATH)
        with open(USER_PLAN_PATH, "r") as f:
            state = State.from_json_str(f.read())
        # instead of trying to load everything in a second way here, just redirect back to the same
        # page using the url parameters so the code path above gets used
        return flask.redirect(flask.url_for("plan", state_b64=state.to_b64_str()))

    if plot_clicked:
        if state is None:
            raise Exception("no state populated")
        return flask.redirect(flask.url_for("plot", state_b64=state.to_b64_str()))

    return flask.render_template("plan.html", **kwargs)


class PlotNavForm(flask_wtf.FlaskForm):
    plan_button = wtforms.fields.SubmitField(label="Back to Planning")


@app.route("/plot/<state_b64>", methods=["POST", "GET"])
def plot(state_b64: str):
    # state must be well formed for this page to work at all
    state = State.from_b64_str(state_b64)

    nav_form = PlotNavForm()

    kwargs = {
        "nav_form": nav_form,
    }

    if nav_form.plan_button.data:
        # go back with the current plan in the editor
        # FIXME: if editing functionality ever added, will need to send b64 from state, not
        # from the original arg
        return flask.redirect(flask.url_for("plan", state_b64=state_b64))

    try:
        input_plan = cenote.plan_from_dict(state.plan)
        output_plan = bungee.replan(input_plan)
        result = cenote.get_result(output_plan)
    except Exception as exc:
        flask.flash("There's a problem with your dive plan:\n{}".format(traceback.format_exc()))
        return flask.render_template("plot.html", **kwargs)

    plan_table_df = plots.get_plan_df(output_plan)
    kwargs["plan_table"] = pretty_html_table.build_table(
        plan_table_df,
        "green_dark",
        odd_bg_color="#242329",
        even_bg_color="#282828",
        even_color="white",
    )

    figs = [
        plots.get_depth_fig(result),
        plots.get_pressure_fig(result),
        plots.get_gradient_fig(result)
        # plots.get_compartment_fig(result)
    ]
    bokeh_theme = bokeh.themes.Theme(
        os.path.join(os.path.dirname(__file__), "static", "bokeh_monokai_theme.yaml")
    )
    kwargs["bokeh_script"], kwargs["bokeh_divs"] = bokeh.embed.components(figs, theme=bokeh_theme)
    kwargs["bokeh_resources"] = bokeh.resources.INLINE.render()

    return flask.render_template("plot.html", **kwargs)


# pick up config variables
app.config.from_object(__name__)
codemirror = flask_codemirror.CodeMirror(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True, use_reloader=True)
