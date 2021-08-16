import uuid

from markupsafe import Markup, escape
from wtforms import StringField
from wtforms.widgets.core import html_params


class TrixWidget:
    def __call__(self, field, **kwargs):
        id = uuid.uuid4()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        html = [
            "<input %s>"
            % html_params(
                type="hidden", name=field.name, id=id, value=escape(field._value())
            ),
        ]

        html.append(
            "<trix-editor %s></trix-editor>"
            % html_params(input=id, name=field.name, **kwargs)
        )
        return Markup("".join(html))


class RichField(StringField):
    widget = TrixWidget()
