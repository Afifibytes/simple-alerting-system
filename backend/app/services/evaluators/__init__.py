from app.services.evaluators.base import EvaluatorRegistry
from app.services.evaluators.conditions import (
    CountConditionEvaluator,
    ThresholdConditionEvaluator,
)

# Register all evaluators
evaluator_registry = EvaluatorRegistry()
evaluator_registry.register("count", CountConditionEvaluator())
evaluator_registry.register("threshold", ThresholdConditionEvaluator())

__all__ = ["evaluator_registry", "EvaluatorRegistry"]
