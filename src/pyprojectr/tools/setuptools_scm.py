import attrs

from pyprojectr.core import PyProjectTool


@attrs.define(frozen=True)
class PyProjectScmTool(PyProjectTool):
    __pyprojectr_no_rename__ = True
    version_scheme: str | None = None
    local_scheme: str | None = None
    write_to: str | None = None
    write_to_template: str | None = None
    relative_to: str | None = None
    tag_regex: str | None = None
    parentdir_prefix: str | None = None
    fallback_version: str | None = None
    parse: str | None = None
    git_describe_command: str | None = None


@attrs.define(frozen=True)
class PyProjectScmxTool(PyProjectTool):
    __pyprojectr_no_rename__ = True
    ci_version_variable: str
    ci_main_branch_name: str
