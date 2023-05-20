#!/usr/bin/env python3
import sys
import os
import traceback

import flask
import flask_wtf
import flask_codemirror
import flask_codemirror.fields
import wtforms

import bokeh.embed
import bokeh.resources

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


class Form(flask_wtf.FlaskForm):
    input_text = flask_codemirror.fields.CodeMirrorField(
        language="yaml",
        config={"lineNumbers": "true"},
    )
    open_button = wtforms.fields.SubmitField(label="Open")
    plan_button = wtforms.fields.SubmitField(label="Plan")
    save_button = wtforms.fields.SubmitField(label="Save")


app = flask.Flask(__name__)


# def setup_plots() -> None:
#     cenote.UREG.setup_matplotlib(True)
#     cenote.UREG.mpl_formatter = "{:~P}"
#     plt.style.use("dark_background")


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

        plan_table_df = plots.get_plan_df(output_plan)
        kwargs["plan_table"] = pretty_html_table.build_table(
            plan_table_df,
            "green_dark",
            odd_bg_color="#242329",
            even_bg_color="#272822",
            even_color="white",
        )

        figs = [
            plots.get_depth_fig(result),
            plots.get_pressure_fig(result),
            # plots.get_gradient_fig(result)
            # plots.get_compartment_fig(result)
        ]
        kwargs["bokeh_script"], kwargs["bokeh_divs"] = bokeh.embed.components(figs)
        kwargs["bokeh_resources"] = bokeh.resources.INLINE.render()

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
    app.run(host="0.0.0.0", port=8888, debug=True, use_reloader=True)
