from typing import TypedDict


class GeneratorConfig(TypedDict, total=False):
    system: str
    user_template: str
    model_name: str
    temperature: float


class DatasetConfig(TypedDict):
    categories: list[str]
    user_bases: list[str]
    document_types: list[str]
    number_of_tools: int
    docs_per_tool: int
