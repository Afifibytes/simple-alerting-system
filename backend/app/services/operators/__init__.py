from app.services.operators.base import OperatorRegistry
from app.services.operators.comparison import (
    ContainsOperator,
    EqualsOperator,
    GreaterThanOperator,
    LessThanOperator,
    GreaterThanOrEqualOperator,
    LessThanOrEqualOperator,
)

# Register all operators (with symbol aliases)
operator_registry = OperatorRegistry()
operator_registry.register("contains", ContainsOperator())
operator_registry.register("eq", EqualsOperator())
operator_registry.register("==", EqualsOperator())
operator_registry.register("gt", GreaterThanOperator())
operator_registry.register(">", GreaterThanOperator())
operator_registry.register("lt", LessThanOperator())
operator_registry.register("<", LessThanOperator())
operator_registry.register("gte", GreaterThanOrEqualOperator())
operator_registry.register(">=", GreaterThanOrEqualOperator())
operator_registry.register("lte", LessThanOrEqualOperator())
operator_registry.register("<=", LessThanOrEqualOperator())

__all__ = ["operator_registry", "OperatorRegistry"]
