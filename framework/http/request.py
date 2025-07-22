from typing import Callable, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Request:
    url: str
    callback: Callable
    meta: Dict[str, Any] = field(default_factory=dict)
