# system
import json
import base64
import pprint

# webapp
import plan


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

    TODO: turn this into protobuf, along with input to bungee
    """

    def __init__(self, config: dict, plan: dict):
        self.config = config
        self.plan = plan

    def __str__(self):
        return prettify_json(self.to_json_str())

    @staticmethod
    def from_dict(data: dict):
        return State(data["config"], data["plan"])

    @staticmethod
    def from_json_str(json_str: str):
        return State.from_dict(json.loads(json_str))

    @staticmethod
    def from_b64_str(b64_str: str):
        return State.from_json_str(json_from_base64(b64_str))

    @staticmethod
    def from_forms(config_form: plan.ConfigForm, plan_form: plan.PlanForm):
        data = {
            "config": {"unit": {}},
            "plan": {},
        }

        ## Config

        # time
        data["config"]["unit"]["time"] = config_form.time.data
        # depth
        data["config"]["unit"]["depth"] = config_form.depth.data
        # pressure
        data["config"]["unit"]["pressure"] = config_form.pressure.data
        # volume rate
        data["config"]["unit"]["volume_rate"] = config_form.volume_rate.data

        ## Plan

        # water
        data["plan"]["water"] = plan_form.water.data
        # gf
        data["plan"]["gf"] = {
            "low": plan_form.gf_lo.data,
            "high": plan_form.gf_hi.data,
        }
        # scr
        data["plan"]["scr"] = {
            "work": plan_form.scr_work.data,
            "deco": plan_form.scr_deco.data,
        }
        # tanks
        data["plan"]["tanks"] = {
            # FIXME: name is populated wrong here
            tank.which.data: {
                "type": tank.kind.data,
                "pressure": tank.pressure.data,
                "mix": {
                    "fO2": tank.fO2.data,
                },
            }
            for tank in plan_form.tanks.entries
        }
        # profile
        data["plan"]["profile"] = [
            {
                "tank": segment.tank.data,
                "duration": segment.duration.data,
                "depth": segment.depth.data,
            }
            for segment in plan_form.profile
        ]

        pprint.pprint(data)
        return State.from_dict(data)

    def to_dict(self) -> dict:
        return {
            "config": self.config,
            "plan": self.plan,
        }

    def to_json_str(self) -> str:
        # FIXME: json dump/parse/dump can be simplified to be faster
        return minify_json(json.dumps(self.to_dict()))

    def to_b64_str(self) -> str:
        return base64_from_json(self.to_json_str())

    def to_forms(self, config_form: plan.ConfigForm, plan_form: plan.PlanForm):

        ## Config

        # time
        config_form.time.data = self.config["unit"]["time"]
        # depth
        config_form.depth.data = self.config["unit"]["depth"]
        # pressure
        config_form.pressure.data = self.config["unit"]["pressure"]
        # volume rate
        config_form.volume_rate.data = self.config["unit"]["volume_rate"]

        ## Plan

        # water
        form.water.data = self.plan["water"]

        # gf
        form.gf_lo.data = self.plan["gf"]["low"]
        form.gf_hi.data = self.plan["gf"]["high"]

        # scr
        form.scr_work.data = self.plan["scr"]["work"]
        form.scr_deco.data = self.plan["scr"]["deco"]

        # tanks
        # first remove all existing tanks
        while len(form.tanks.entries) > 1:
            form.tanks.pop_entry()
        # now populate
        for name in self.plan["tanks"].keys():
            form.tanks.entries[-1].which.data = name
            form.tanks.entries[-1].kind.data = self.plan["tanks"][name]["type"]
            form.tanks.entries[-1].pressure.data = self.plan["tanks"][name]["pressure"]
            form.tanks.entries[-1].fO2.data = self.plan["tanks"][name]["mix"]["fO2"]
            if len(self.plan["tanks"]) > len(form.tanks.entries):
                form.tanks.append_entry()

        # profile
        # first remove all existing segments
        while len(form.profile.entries) > 1:
            form.profile.pop_entry()
        # now populate
        for segment in self.plan["profile"]:
            form.profile.entries[-1].tank.data = segment["tank"]
            form.profile.entries[-1].duration.data = segment["duration"]
            form.profile.entries[-1].depth.data = segment["depth"]
            if len(self.plan["profile"]) > len(form.profile.entries):
                form.profile.append_entry()
