"""Base class for all Astera Value Objects."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AsteraValueObject:
    """
    Base for all Value Objects in the Astera domain.

    Value objects are:
        - Immutable (frozen=True)
        - Identity-free (equality by value, not by id)
        - Self-validating (validate in __post_init__)
    """
