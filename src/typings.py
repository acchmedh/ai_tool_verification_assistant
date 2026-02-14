from typing import TypedDict

class GeneratorConfig(TypedDict, total=False):
    SYSTEM: str
    USER_TEMPLATE: str
    MODEL_NAME: str
    TEMPERATURE: float
    NUMBER_OF_TOOLS: int
