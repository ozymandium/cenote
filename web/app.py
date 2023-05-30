#!/usr/bin/env python3
# system
import os

# pip deps
import flask
import bokeh.embed
import bokeh.resources
import bokeh.themes
import pretty_html_table

# in the webapp
import plot
import plan
from state import State

# elsewhere
import bungee
import cenote


SECRET_KEY = "secret!"

# ermagerd what if more than one person uses it?
# lol that'll never happen
USER_PLAN_PATH = "/tmp/user_plan.json"


class Webapp:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.app.config.from_object(__name__)
        self.app.add_url_rule(
            "/plan", methods=["GET", "POST"], defaults={"state_b64": None}, view_func=self.plan
        )
        self.app.add_url_rule("/plan/<state_b64>", methods=["GET", "POST"], view_func=self.plan)
        self.app.add_url_rule("/plot/<state_b64>", methods=["POST", "GET"], view_func=self.plot)

    def run(self, host="0.0.0.0", port=8888, debug=True, use_reloader=True):
        self.app.run(host=host, port=port, debug=debug, use_reloader=use_reloader)

    @staticmethod
    def plan(state_b64: str):
        # create forms
        upload_form = plan.UploadForm()
        plan_form = plan.PlanForm()

        print(plan_form.tanks[0].kind)
        print(plan_form.tanks[0].kind.data)

        # parse url arguments
        if state_b64 is not None:
            state = State.from_b64_str(state_b64)
            state.to_forms(plan_form)

        kwargs = {
            "upload_form": upload_form,
            "plan_form": plan_form,
        }

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
            state = State.from_forms(plan_form)
            return flask.redirect(flask.url_for("plot", state_b64=state.to_b64_str()))

        # save
        if plan_form.save_button.data:
            state = State.from_forms(plan_form)
            json_str = prettify_json(state.to_json_str())
            with open(USER_PLAN_PATH, "w") as f:
                f.write(json_str)
            return flask.send_file(
                USER_PLAN_PATH, as_attachment=True, download_name="kalousac.json"
            )

        return flask.render_template("plan.html", **kwargs)

    @staticmethod
    def plot(state_b64: str):
        # state must be well formed for this page to work at all
        state = State.from_b64_str(state_b64)
        # TODO: logging instead
        print("Received state:\n{}".format(str(state)))
        nav_form = plot.NavForm()
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

        plan_table_df = plot.get_plan_df(
            output_plan,
            time_unit=state.config["unit"]["time"],
            depth_unit=state.config["unit"]["depth"],
        )
        kwargs["plan_table"] = pretty_html_table.build_table(
            plan_table_df,
            "green_dark",
            odd_bg_color="#242329",
            even_bg_color="#282828",
            even_color="white",
        )
        figs = [
            plot.get_depth_fig(
                result,
                time_unit=state.config["unit"]["time"],
                depth_unit=state.config["unit"]["depth"],
            ),
            plot.get_pressure_fig(
                result,
                time_unit=state.config["unit"]["time"],
                pressure_unit=state.config["unit"]["pressure"],
            ),
            plot.get_gradient_fig(result, time_unit=state.config["unit"]["time"]),
            # plot.get_compartment_fig(result)
        ]
        bokeh_theme = bokeh.themes.Theme(
            os.path.join(os.path.dirname(__file__), "static", "bokeh_monokai_theme.yaml")
        )
        kwargs["bokeh_script"], kwargs["bokeh_divs"] = bokeh.embed.components(
            figs, theme=bokeh_theme
        )
        kwargs["bokeh_resources"] = bokeh.resources.INLINE.render()

        return flask.render_template("plot.html", **kwargs)


if __name__ == "__main__":
    webapp = Webapp()
    webapp.run()
