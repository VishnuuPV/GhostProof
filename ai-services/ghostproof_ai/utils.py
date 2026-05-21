from __future__ import annotations

import base64
import hashlib
import json
import math
import re
from typing import Any


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, default=str, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def decode_data_url(value: str | None) -> bytes | None:
    if not value:
        return None
    match = re.match(r"^data:[^;]+;base64,(?P<body>.+)$", value, flags=re.DOTALL)
    if not match:
        return None
    try:
        return base64.b64decode(match.group("body"), validate=True)
    except Exception:
        return None


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number
