import bungee
import pint

UREG = pint.UnitRegistry()

DEPTH_UNIT = UREG.parse_expression(bungee.get_depth_unit_str()).units
PRESSURE_UNIT = UREG.parse_expression(bungee.get_pressure_unit_str()).units
TIME_UNIT = UREG.parse_expression(bungee.get_time_unit_str()).units
VOLUME_RATE_UNIT = UREG.parse_expression(bungee.get_volume_rate_unit_str()).units
