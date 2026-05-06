from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from shared.scripts.paper_research_common import read_json
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    from paper_research_common import read_json


TYPE_MAP = {
    "array": list,
    "boolean": bool,
    "integer": int,
    "null": type(None),
    "object": dict,
    "string": str,
}


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, TYPE_MAP[expected])


def _validate(data: Any, schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []

    if "type" in schema:
        expected_types = schema["type"]
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(_type_matches(data, expected) for expected in expected_types):
            errors.append(f"{path}: expected type {'|'.join(expected_types)}")
            return errors

    if "enum" in schema and data not in schema["enum"]:
        allowed = ", ".join(str(item) for item in schema["enum"])
        errors.append(f"{path}: expected one of {allowed}")

    if isinstance(data, dict):
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"{path}.{field}: missing required field")

        properties = schema.get("properties", {})
        for field, value in data.items():
            if field in properties:
                errors.extend(_validate(value, properties[field], f"{path}.{field}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}.{field}: unexpected field")

    if isinstance(data, list) and "items" in schema:
        item_schema = schema["items"]
        for index, item in enumerate(data):
            errors.extend(_validate(item, item_schema, f"{path}[{index}]"))

    return errors


def validate_memory(data: dict[str, Any], schema_path: Path) -> list[str]:
    schema = read_json(schema_path)
    return _validate(data, schema, "$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a paper memory JSON file.")
    parser.add_argument("memory", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "schemas" / "paper-memory.schema.json",
    )
    args = parser.parse_args()

    errors = validate_memory(read_json(args.memory), args.schema)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
