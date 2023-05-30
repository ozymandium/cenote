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
    def from_forms(plan_form: plan.PlanForm):
        data = {
            "config": {"unit": {}},
            "plan": {},
        }

        ## Config

        # time
        data["config"]["unit"]["time"] = plan_form.time_unit.data
        # depth
        data["config"]["unit"]["depth"] = plan_form.depth_unit.data
        # pressure
        data["config"]["unit"]["pressure"] = plan_form.pressure_unit.data
        # volume rate
        data["config"]["unit"]["volume_rate"] = plan_form.volume_rate_unit.data

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

    def to_forms(self, plan_form: plan.PlanForm):
        ## Config

        # time
        plan_form.time_unit.data = self.config["unit"]["time"]
        # depth
        plan_form.depth_unit.data = self.config["unit"]["depth"]
        # pressure
        plan_form.pressure_unit.data = self.config["unit"]["pressure"]
        # volume rate
        plan_form.volume_rate_unit.data = self.config["unit"]["volume_rate"]

        ## Plan

        # water
        plan_form.water.data = self.plan["water"]

        # gf
        plan_form.gf_lo.data = self.plan["gf"]["low"]
        plan_form.gf_hi.data = self.plan["gf"]["high"]

        # scr
        plan_form.scr_work.data = self.plan["scr"]["work"]
        plan_form.scr_deco.data = self.plan["scr"]["deco"]

        # tanks
        # first remove all existing tanks
        while len(plan_form.tanks.entries) > 1:
            plan_form.tanks.pop_entry()
        # now populate
        for name in self.plan["tanks"].keys():
            plan_form.tanks.entries[-1].which.data = name
            plan_form.tanks.entries[-1].kind.data = self.plan["tanks"][name]["type"]
            plan_form.tanks.entries[-1].pressure.data = self.plan["tanks"][name]["pressure"]
            plan_form.tanks.entries[-1].fO2.data = self.plan["tanks"][name]["mix"]["fO2"]
            if len(self.plan["tanks"]) > len(plan_form.tanks.entries):
                plan_form.tanks.append_entry()

        # profile
        # first remove all existing segments
        while len(plan_form.profile.entries) > 1:
            plan_form.profile.pop_entry()
        # now populate
        for segment in self.plan["profile"]:
            plan_form.profile.entries[-1].tank.data = segment["tank"]
            plan_form.profile.entries[-1].duration.data = segment["duration"]
            plan_form.profile.entries[-1].depth.data = segment["depth"]
            if len(self.plan["profile"]) > len(plan_form.profile.entries):
                plan_form.profile.append_entry()
