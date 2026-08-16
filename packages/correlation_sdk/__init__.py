"""Provider-neutral contracts for the Astera Correlation Pipeline."""

from .in_memory import SharedTermCorrelationEngine
from .models import Correlation, CorrelationBatch
from .protocol import CorrelationEngine

__all__ = ["Correlation", "CorrelationBatch", "CorrelationEngine", "SharedTermCorrelationEngine"]
