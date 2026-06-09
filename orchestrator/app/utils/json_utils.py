import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract first JSON object from LLM response."""
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))

    brace = re.search(r"\{.*\}", text, re.DOTALL)
    if brace:
        return json.loads(brace.group(0))

    raise ValueError("No JSON object found in model response")


def parse_structured(model_cls: type[T], text: str) -> T:
    data = extract_json_object(text)
    return model_cls.model_validate(data)
