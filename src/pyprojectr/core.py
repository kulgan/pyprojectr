from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

import attrs
import cattrs
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn

T = TypeVar("T")
D = TypeVar("D")
STRUCT_CONVERTER = cattrs.Converter()


def convert_underscores(cls: type[T]) -> cattrs.SimpleStructureHook[Mapping[str, Any], T]:
    no_rename_cls = getattr(cls, "__pyprojectr_no_rename__", False)
    overrides = {}
    for a in attrs.fields(cls):
        if no_rename_cls or a.metadata.get("pyprojectr_no_rename"):
            continue
        overrides[a.name] = cattrs.override(rename=_underscores_to_hyphen(a.name))
    return make_dict_structure_fn(cls, STRUCT_CONVERTER, **overrides)


def unconvert_underscores(cls: type[T]) -> Any:
    no_rename_cls = getattr(cls, "__pyprojectr_no_rename__", False)
    overrides = {}
    for a in attrs.fields(cls):
        if no_rename_cls or a.metadata.get("pyprojectr_no_rename"):
            continue
        overrides[a.name] = cattrs.override(rename=_underscores_to_hyphen(a.name))
    return make_dict_unstructure_fn(cls, STRUCT_CONVERTER, **overrides)


def _underscores_to_hyphen(text: str, reverse: bool = False) -> str:
    if not reverse:
        return text.replace("_", "-")
    return text.replace("-", "_")


@attrs.define
class BaseModel:
    @classmethod
    def converter(cls) -> cattrs.Converter:
        return STRUCT_CONVERTER

    @classmethod
    def from_data(cls, data: D) -> Self:
        return cls.converter().structure(data, cls)

    def to_data(self) -> dict[str, Any]:
        return self.converter().unstructure(self)


STRUCT_CONVERTER.register_structure_hook_factory(attrs.has, convert_underscores)
STRUCT_CONVERTER.register_unstructure_hook_factory(attrs.has, unconvert_underscores)


class PyProjectTool(BaseModel): ...
