#!/usr/bin/env python3
import sys
import os
import traceback

import flask
import flask_wtf
import flask_codemirror
import flask_codemirror.fields
import wtforms

import plots
import bungee
import cenote


SECRET_KEY = "secret!"
# mandatory
CODEMIRROR_LANGUAGES = ["yaml"]
# optional
CODEMIRROR_THEME = "monokai"
CODEMIRROR_ADDONS = (("display", "placeholder"),)


app = flask.Flask(__name__)


class Form(flask_wtf.FlaskForm):
    input_text = flask_codemirror.fields.CodeMirrorField(
        language="yaml",
        config={"lineNumbers": "true"},
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
        # if empty, load a default config with helpful comments
        with open(os.path.join(os.path.dirname(__file__), "..", "examples", "big.yaml"), "r") as f:
            form.input_text.data = f.read()
        return flask.render_template("index.html", **kwargs)

    if plan_clicked:
        try:
            input_plan = cenote.get_plan(input_text, is_path=False)
            output_plan = bungee.replan(input_plan)
            result = cenote.get_result(output_plan)
        except Exception as exc:
            flask.flash("There's a problem with your dive plan:\n{}".format(traceback.format_exc()))
            return flask.render_template("index.html", **kwargs)

        kwargs["plan_table"] = plots.get_plan_table_html(output_plan)
        kwargs["depth_plot"] = plots.get_depth_plot_html(result)
        kwargs["pressure_plot"] = plots.get_pressure_plot_html(result)
        kwargs["gradient_plot"] = plots.get_gradient_plot_html(result)
        kwargs["compartment_plot"] = plots.get_compartment_plot_html(result)

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
    plots.setup_plots()
    app.run(host="0.0.0.0", port=8888, debug=True, use_reloader=True)
