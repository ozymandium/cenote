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


class EditorForm(flask_wtf.FlaskForm):
    input_text = flask_codemirror.fields.CodeMirrorField(
        language="json",
        config={"lineNumbers": "true"},
    )
    plan_button = wtforms.fields.SubmitField(label="Plan")
    save_button = wtforms.fields.SubmitField(label="Save")


class UploadForm(flask_wtf.FlaskForm):
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


app = flask.Flask(__name__)

# def setup_plots() -> None:
#     cenote.UREG.setup_matplotlib(True)
#     cenote.UREG.mpl_formatter = "{:~P}"
#     plt.style.use("dark_background")


@app.route("/<plan_base64_blob>", methods=["GET", "POST"])
def index(plan_base64_blob=None):
    # create forms
    upload_form = UploadForm()
    editor_form = EditorForm()

    # harvest information from forms
    upload_json = upload_form.file_picker.data
    upload_clicked = upload_form.upload_button.data
    input_text = editor_form.input_text.data
    plan_clicked = editor_form.plan_button.data
    save_clicked = editor_form.save_button.data

    # start jinja template args to render
    kwargs = {}
    kwargs["editor_form"] = editor_form
    kwargs["upload_form"] = upload_form

    empty_editor = (input_text is None) or (len(input_text) == 0)

    if empty_editor:
        if plan_base64_blob is None:
            # if empty, load a default config with helpful comments
            with open(
                os.path.join(os.path.dirname(__file__), "..", "examples", "big.json"), "r"
            ) as f:
                editor_form.input_text.data = f.read()
        else:
            # nothing in the text editor but blob in the url
            json_blob = json_from_base64(plan_base64_blob)
            editor_form.input_text.data = prettify_json(json_blob)

    if upload_clicked and upload_json is not None:
        # it will be of type FileStorage
        # path = werkzeug.utils.secure_filename(upload_json.filename)
        upload_json.save(USER_PLAN_PATH)
        with open(USER_PLAN_PATH, "r") as f:
            editor_form.input_text.data = f.read()
        return flask.render_template("index.html", **kwargs)

    if plan_clicked:
        base64_blob = base64_from_json(input_text)
        return flask.redirect(flask.url_for("plot", plan_base64_blob=base64_blob))

    elif save_clicked:
        with open(USER_PLAN_PATH, "w") as f:
            f.write(editor_form.input_text.data)
        return flask.send_file(
            USER_PLAN_PATH, as_attachment=True, download_name="there_is_room_in_the_kalousac.json"
        )

    else:
        return flask.render_template("index.html", **kwargs)


class BackToEditForm(flask_wtf.FlaskForm):
    edit_button = wtforms.fields.SubmitField(label="Back to Editing")


@app.route("/plot/<plan_base64_blob>", methods=["POST", "GET"])
def plot(plan_base64_blob: str):
    if plan_base64_blob is None:
        return "you didn't send plan data"

    json_blob = json_from_base64(plan_base64_blob)

    back_to_edit_form = BackToEditForm()

    kwargs = {
        "back_to_edit_form": back_to_edit_form,
    }

    if back_to_edit_form.edit_button.data:
        # go back with the current plan in the editor
        return flask.redirect(flask.url_for("index", plan_base64_blob=plan_base64_blob))

    try:
        input_plan = cenote.parse_plan(json_blob)
        output_plan = bungee.replan(input_plan)
        result = cenote.get_result(output_plan)
    except Exception as exc:
        flask.flash("There's a problem with your dive plan:\n{}".format(traceback.format_exc()))
        return flask.render_template("plot.html", **kwargs)

    # sending a new page so clear the kwargs of the unnecesary forms?
    # kwargs = {}

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
