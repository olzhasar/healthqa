import uuid

from markupsafe import Markup, escape
from wtforms import Field, SelectMultipleField, StringField
from wtforms.widgets.core import html_params


class TrixWidget:
    def __call__(self, field: Field, **kwargs):
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


class TagsWidget:
    def __call__(self, field: Field, **kwargs):
        field_id = kwargs.pop("id", field.id)
        html = []
        for value, label, checked in field.iter_choices():
            choice_id = f"{field_id}-{value}"

            options = dict(type="checkbox", name=field.name, value=value, id=choice_id)
            if checked:
                options["checked"] = "checked"

            html.append("<div>")
            html.append('<label class="inline-flex items-center">')
            html.append("<input %s>" % html_params(**options))
            html.append(f'<span class="ml-2">{label}</span>')
            html.append("</label>")
            html.append("</div>")
        return Markup("".join(html))


class TagsField(SelectMultipleField):
    widget = TagsWidget()

    def process_data(self, value):
        try:
            self.data = [tag.id for tag in value]
        except TypeError:
            self.data = None
