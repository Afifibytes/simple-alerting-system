from typing import Optional

from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    triggered: bool
    matches: Optional[int] = None
    threshold: int
    message: Optional[str] = None
