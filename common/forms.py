import uuid

from markupsafe import Markup, escape
from wtforms import StringField
from wtforms.widgets.core import html_params


class TrixWidget:
    def __call__(self, field, **kwargs):
        id = uuid.uuid4()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        markup = (
            f'<input type="hidden" name="{field.name}" id="{id}" value="{escape(field._value())}">'
            + f'<trix-editor input="{id}" html_params(name=field.name, **kwargs)></trix-editor>'
        )
        return Markup(markup)


class RichField(StringField):
    widget = TrixWidget()
