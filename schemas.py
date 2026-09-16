# Pydantic request/response models
from pydantic import BaseModel
from typing import List, Optional

class BrandInfo(BaseModel):
    name: str
    detected_from_logo: bool
    confidence: str

class DressAnalysisResult(BaseModel):
    garment_type: str
    gender: str
    primary_color: str
    secondary_colors: List[str] = []
    pattern: str
    brand: BrandInfo
    notes: Optional[str] = None

class AnalyzeResponse(BaseModel):
    success: bool
    filename: str
    analysis: Optional[DressAnalysisResult] = None
    error: Optional[str] = None
    