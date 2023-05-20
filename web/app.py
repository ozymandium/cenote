#!/usr/bin/env python3
import sys
import os
import traceback

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
CODEMIRROR_LANGUAGES = ["yaml"]
# optional
CODEMIRROR_THEME = "monokai"
CODEMIRROR_ADDONS = (("display", "placeholder"),)

# ermagerd what if more than one person uses it?
# lol that'll never happen
USER_PLAN_PATH = "/tmp/user_plan.yaml"


class EditorForm(flask_wtf.FlaskForm):
    input_text = flask_codemirror.fields.CodeMirrorField(
        language="yaml",
        config={"lineNumbers": "true"},
    )
    plan_button = wtforms.fields.SubmitField(label="Plan")
    save_button = wtforms.fields.SubmitField(label="Save")


class UploadForm(flask_wtf.FlaskForm):
    file_picker = flask_wtf.file.FileField(
        validators=[
            flask_wtf.file.FileRequired(),
            flask_wtf.file.FileAllowed(["yml", "yaml"], "Only YAML files are supported."),
        ]
    )
    upload_button = wtforms.fields.SubmitField(label="Upload")


app = flask.Flask(__name__)


# def setup_plots() -> None:
#     cenote.UREG.setup_matplotlib(True)
#     cenote.UREG.mpl_formatter = "{:~P}"
#     plt.style.use("dark_background")


@app.route("/", methods=["GET", "POST"])
def index():
    # create forms
    upload_form = UploadForm()
    editor_form = EditorForm()

    # harvest information from forms
    upload_yaml = upload_form.file_picker.data
    upload_clicked = upload_form.upload_button.data
    input_text = editor_form.input_text.data
    plan_clicked = editor_form.plan_button.data
    save_clicked = editor_form.save_button.data

    # start jinja template args to render
    kwargs = {}
    kwargs["editor_form"] = editor_form
    kwargs["upload_form"] = upload_form

    if input_text is None or len(input_text) == 0:
        # if empty, load a default config with helpful comments
        with open(os.path.join(os.path.dirname(__file__), "..", "examples", "big.yaml"), "r") as f:
            editor_form.input_text.data = f.read()
        # return flask.render_template("index.html", **kwargs)

    if upload_clicked and upload_yaml is not None:
        # it will be of type FileStorage
        # path = werkzeug.utils.secure_filename(upload_yaml.filename)
        upload_yaml.save(USER_PLAN_PATH)
        with open(USER_PLAN_PATH, "r") as f:
            editor_form.input_text.data = f.read()
        return flask.render_template("index.html", **kwargs)

    if plan_clicked:
        try:
            input_plan = cenote.get_plan(input_text, is_path=False)
            output_plan = bungee.replan(input_plan)
            result = cenote.get_result(output_plan)
        except Exception as exc:
            flask.flash("There's a problem with your dive plan:\n{}".format(traceback.format_exc()))
            return flask.render_template("index.html", **kwargs)

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
        kwargs["bokeh_script"], kwargs["bokeh_divs"] = bokeh.embed.components(
            figs, theme=bokeh_theme
        )
        kwargs["bokeh_resources"] = bokeh.resources.INLINE.render()

        return flask.render_template("index.html", **kwargs)

    elif save_clicked:
        with open(USER_PLAN_PATH, "w") as f:
            f.write(editor_form.input_text.data)
        return flask.send_file(
            USER_PLAN_PATH, as_attachment=True, download_name="there_is_room_in_the_kalousac.yaml"
        )
        return flask.render_template("index.html", **kwargs)

    else:
        return flask.render_template("index.html", **kwargs)


# pick up config variables
app.config.from_object(__name__)
codemirror = flask_codemirror.CodeMirror(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True, use_reloader=True)
