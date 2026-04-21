import attrs
import cattrs
from cattrs.gen import make_dict_structure_fn

STRUCT_CONVERTER = cattrs.Converter()


def convert_underscores(cls):
    return make_dict_structure_fn(
        cls,
        STRUCT_CONVERTER,
        **{a.name: cattrs.override(rename=_underscores_to_hyphen(a.name)) for a in attrs.fields(cls)},
    )


def _underscores_to_hyphen(text: str, reverse: bool = False) -> str:
    if not reverse:
        return text.replace("_", "-")
    return text.replace("-", "_")


@attrs.define
class BaseModel:
    @classmethod
    def converter(cls) -> cattrs.Converter:
        return STRUCT_CONVERTER


STRUCT_CONVERTER.register_structure_hook_factory(attrs.has, convert_underscores)
