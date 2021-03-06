from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Iterator, List, Tuple

from markupsafe import Markup, escape
from wtforms import Field, SelectMultipleField, StringField
from wtforms.widgets.core import html_params

if TYPE_CHECKING:
    from wtforms.form import Form

    from models import Tag, TagCategory


class TrixWidget:
    def __call__(self, field: Field, **kwargs: Any) -> Markup:
        id = uuid.uuid4()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        html = [
            "<input %s>"
            % html_params(
                type="hidden", name=field.name, id=id, value=escape(field._value())
            ),
        ]

        kwargs["class"] += " " + " ".join(
            [
                "trix",
                "appearance-none",
                "text-grey-darker",
                "py-2",
                "px-4",
                "border",
                "border-gray-300",
                "focus:ring",
                "ring-green-500",
            ]
        )

        html.append(
            "<trix-editor %s></trix-editor>"
            % html_params(input=id, name=field.name, **kwargs)
        )
        return Markup("".join(html))


class RichField(StringField):
    widget = TrixWidget()


class ChoiceCategory:
    def __init__(self, instance: TagCategory, data: list[int]):
        self._instance = instance
        self.data = data

    @property
    def name(self) -> str:
        return self._instance.name

    def iter_tags(self) -> Iterator[Tuple[int, str, bool]]:
        for tag in self._instance.tags:
            selected = self.data is not None and tag.id in self.data
            yield tag.id, tag.name, selected


class TagsWidget:
    def __call__(self, field: Field, **kwargs: Any) -> Markup:
        field_id = kwargs.pop("id", field.id)
        html = ["<div>"]
        for category in field.iter_categories():
            html.append('<div class="p-4 rounded border mb-4">')
            html.append(f'<p class="text-gray-500 font-bold mb-4">{category.name}</p>')
            html.append('<div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">')

            for value, label, checked in category.iter_tags():
                choice_id = f"{field_id}-{value}"

                options = dict(
                    type="checkbox", name=field.name, value=value, id=choice_id
                )
                if checked:
                    options["checked"] = "checked"

                html.append("<div>")
                html.append('<label class="inline-flex items-center">')
                html.append("<input %s>" % html_params(**options))
                html.append(f'<span class="ml-2">{label}</span>')
                html.append("</label>")
                html.append("</div>")
            html.append("</div>")
            html.append("</div>")
        html.append("</div>")
        return Markup("".join(html))


class TagsField(SelectMultipleField):
    widget = TagsWidget()

    def process_data(self, value: List[Tag]) -> None:
        try:
            self.data = [tag.id for tag in value]
        except TypeError:
            self.data = None

    def iter_categories(self) -> Iterator[ChoiceCategory]:
        for category in self.choices:
            yield ChoiceCategory(category, self.data)

    def pre_validate(self, form: Form) -> None:
        if self.data:
            values = []
            for category in self.choices:
                for tag in category.tags:
                    values.append(tag.id)

            for d in self.data:
                if d not in values:
                    raise ValueError(
                        self.gettext("'%(value)s' is not a valid choice for this field")
                        % dict(value=d)
                    )
