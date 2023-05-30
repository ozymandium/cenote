import flask_wtf
import flask_wtf.file
import wtforms

import bungee


class TankSubform(wtforms.Form):
    # "name" field means something else
    which = wtforms.fields.StringField(
        "Name",
        default="Primary",
        validators=[
            wtforms.validators.DataRequired(),
        ],
    )
    # "type" field means something else
    kind = wtforms.fields.SelectField(
        "Type",
        default="AL80",
        choices=[
            (bungee.Tank(i).name, bungee.Tank(i).name) for i in range(bungee.Tank.COUNT.value)
        ],
    )
    fO2 = wtforms.fields.FloatField(
        "O2 Fraction",
        default=0.21,
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.NumberRange(min=0.0, max=1.0),
        ],
    )
    pressure = wtforms.fields.StringField(
        "Start Pressure",
        default="3000 psi",
        validators=[
            # FIXME: custom validator to make sure that pint unit exists
            wtforms.validators.DataRequired()
        ],
    )


class ProfileSubform(wtforms.Form):
    # TODO: make this a select field with dynamic choices from tank names
    # see example here: https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.SelectField
    tank = wtforms.fields.StringField(
        "Tank at Start", default="Primary", validators=[wtforms.validators.Optional()]
    )
    duration = wtforms.fields.StringField(
        "Duration", default="5 min", validators=[wtforms.validators.DataRequired()]
    )
    depth = wtforms.fields.StringField(
        "Final Depth", default="20 ft", validators=[wtforms.validators.DataRequired()]
    )


class PlanForm(flask_wtf.FlaskForm):
    time_unit = wtforms.fields.SelectField(
        "Time unit",
        default="minute",
        choices=[
            "minute",
            "second",
            "hour",
        ],
    )
    depth_unit = wtforms.fields.SelectField(
        "Depth unit",
        default="foot",
        choices=[
            "foot",
            "meter",
            "inch",
            "yard",
        ],
    )
    pressure_unit = wtforms.fields.SelectField(
        "Pressure unit",
        default="psi",
        choices=[
            "psi",
            "bar",
        ],
    )
    volume_rate_unit = wtforms.fields.SelectField(
        "Volume rate unit",
        default="cubic foot per minute",
        choices=[
            "cubic foot per minute",
            "liter per minute",
        ],
    )

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
    # FIXME: custom validator to make sure that pint unit exists
    scr_work = wtforms.fields.StringField(
        default="0.75 ft^3 / min",
        validators=[wtforms.validators.DataRequired()],
    )
    # FIXME: custom validator to make sure that pint unit exists
    scr_deco = wtforms.fields.StringField(
        default="0.55 ft^3 /min",
        validators=[wtforms.validators.DataRequired()],
    )
    plot_button = wtforms.fields.SubmitField(label="Plot")
    save_button = wtforms.fields.SubmitField(label="Save")
    tanks = wtforms.FieldList(wtforms.FormField(TankSubform), min_entries=1, max_entries=4)
    add_tank = wtforms.fields.SubmitField(label="Add Tank")
    remove_tank = wtforms.fields.SubmitField(label="Remove Tank")
    profile = wtforms.FieldList(wtforms.FormField(ProfileSubform), min_entries=1, max_entries=20)
    add_segment = wtforms.fields.SubmitField(label="Add Segment")
    remove_segment = wtforms.fields.SubmitField(label="Remove Segment")


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
