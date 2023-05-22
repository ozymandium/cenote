#!/usr/bin/env python3
import sys
import os
import traceback
import json
import base64

import flask
import flask_wtf
import flask_wtf.file
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


class PlanTankSubform(wtforms.Form):
    name = wtforms.fields.StringField(
        "Name",
        default="Primary",
        validators = [
            wtforms.validators.DataRequired(),
        ]
    )
    kind = wtforms.fields.SelectField(
        "Type",
        default = "AL80",
        choices=[
            (bungee.Tank(i).name, bungee.Tank(i).name)
            for i in range(bungee.Tank.COUNT.value)
        ]
    )
    mix_fO2 = wtforms.fields.FloatField(
        "O2 Fraction",
        default=0.21,
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.NumberRange(min=0.0, max=1.0),
        ],
    )
    pressure = wtforms.fields.StringField(
        "Start Pressure",
        default = "3000 psi",
        validators=[
            # FIXME: custom validator to make sure that pint unit exists
            wtforms.validators.DataRequired()
        ],
    )

class PlanProfileSubform(wtforms.Form):
    tank = wtforms.fields.StringField(
        "Tank at Start",
        default="Primary",
        validators=[wtforms.validators.Optional()]
    )
    duration = wtforms.fields.StringField(
        "Duration",
        default="5 min",
        validators=[wtforms.validators.DataRequired()]
    )
    depth = wtforms.fields.StringField(
        "Final Depth",
        default="20 ft",
        validators=[wtforms.validators.DataRequired()]
    )

class PlanPlanForm(flask_wtf.FlaskForm):
    water = wtforms.fields.SelectField(
        "Water type",
        choices=[
            (bungee.Water(i).name, bungee.Water(i).name.title())
            for i in range(bungee.Water.COUNT.value)
        ],
    )
    gf_lo = wtforms.fields.FloatField(
        default=0.55,
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.NumberRange(min=0.1, max=1.0),
        ],
    )
    gf_hi = wtforms.fields.FloatField(
        default=0.8,
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.NumberRange(min=0.1, max=1.0),
        ],
    )
    scr_work = wtforms.fields.StringField(
        default="0.75 cuft / min",
        validators=[
            # FIXME: custom validator to make sure that pint unit exists
            wtforms.validators.DataRequired()
        ],
    )
    scr_deco = wtforms.fields.StringField(
        default="0.55 cuft /min",
        validators=[
            # FIXME: custom validator to make sure that pint unit exists
            wtforms.validators.DataRequired()
        ],
    )
    plot_button = wtforms.fields.SubmitField(label="Plot")
    save_button = wtforms.fields.SubmitField(label="Save")
    tanks = wtforms.FieldList(
        wtforms.FormField(PlanTankSubform),
        min_entries=1,
        max_entries=4
    )
    add_tank = wtforms.fields.SubmitField(label="Add Tank")
    remove_tank = wtforms.fields.SubmitField(label="Remove Tank")
    profile = wtforms.FieldList(
        wtforms.FormField(PlanProfileSubform),
        min_entries=1,
        max_entries=20
    )
    add_segment = wtforms.fields.SubmitField(label="Add Segment")
    remove_segment = wtforms.fields.SubmitField(label="Remove Segment")

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

    kwargs = {
        "upload_form": upload_form,
        "plan_form": plan_form,
    }

    # parse url arguments
    if state_b64 is not None:
        state = State.from_b64_str(state_b64)
    else:
        state = None

    # upload
    if upload_form.upload_button.data and upload_form.file_picker.data is not None:
        # it will be of type FileStorage
        # path = werkzeug.utils.secure_filename(upload_form.file_picker.data.filename)
        upload_form.file_picker.data.save(USER_PLAN_PATH)
        with open(USER_PLAN_PATH, "r") as f:
            state = State.from_json_str(f.read())
        # instead of trying to load everything in a second way here, just redirect back to the same
        # page using the url parameters so the code path above gets used
        return flask.redirect(flask.url_for("plan", state_b64=state.to_b64_str()))

    # add/remove tank
    # FIXME: fieldlist does not support arbitrary item deletion, find a different approach so
    # we can delete middle elements
    if plan_form.add_tank.data:
        if len(plan_form.tanks) < plan_form.tanks.max_entries:
            plan_form.tanks.append_entry()
    if plan_form.remove_tank.data:
        if len(plan_form.tanks) > plan_form.tanks.min_entries:
            plan_form.tanks.pop_entry()

    # add/remove segment
    # FIXME: fieldlist does not support arbitrary item deletion, find a different approach so
    # we can delete middle elements
    if plan_form.add_segment.data:
        if len(plan_form.profile) < plan_form.profile.max_entries:
            plan_form.profile.append_entry()
    if plan_form.remove_segment.data:
        if len(plan_form.profile) > plan_form.profile.min_entries:
            plan_form.profile.pop_entry()

    # plot
    # FIXME: validate_on_submit???
    if plan_form.plot_button.data:
        if state is None:
            raise Exception("no state populated")
        return flask.redirect(flask.url_for("plot", state_b64=state.to_b64_str()))

    # save
    if plan_form.save_button.data:
        pass

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True, use_reloader=True)
