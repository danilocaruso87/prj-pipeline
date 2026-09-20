from pydantic import BaseModel, Field

class RowInput(BaseModel):
    review: str = Field(..., description="il testo in input per il quale si chiede la Sentiment Analysis")

class DetectionOutput(BaseModel):
    sentiment: str = Field(..., description="sentiment della frase")
    confidence: float = Field(..., description="Probabilità della predizione")