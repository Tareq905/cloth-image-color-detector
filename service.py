# main business logic (image analysis)
import base64
import json
from fastapi import UploadFile
from llm_client import llm_client
from config import settings
from schemas import DressAnalysisResult

ANALYSIS_PROMPT = """You are a fashion image analysis expert. Carefully examine this dress image and respond according to the JSON schema below. Return ONLY valid JSON — no extra text, explanation, or markdown code fences.

JSON schema:
{
  "garment_type": "tshirt | shirt | pant | plazoo | jeans | saree | kurti | dress | skirt | jacket | other",
  "gender": "male | female | unisex",
  "primary_color": "string",
  "secondary_colors": ["string"],
  "pattern": "solid | striped | checked | floral | printed | polka-dot | abstract | other",
  "brand": {
    "name": "string",
    "detected_from_logo": true/false,
    "confidence": "high | medium | low | assumed"
  },
  "notes": "string (mention here if any field is an assumption rather than a confident detection)"
}

Rules:
- If you are not fully certain about any field, give your best guess but lower the confidence to "low" or "assumed".
- For brand: NEVER return "Unknown", "N/A", or leave it empty. If a logo is clearly visible, give the correct brand name, set confidence to "high" or "medium", and set detected_from_logo to true. If no logo is visible or identifiable, infer the most plausible real-world brand based on the garment's style, cut, fabric, stitching pattern, and overall design — pick a well-known brand commonly associated with that style — set confidence to "assumed" and detected_from_logo to false. The brand.name field must never be blank or "Unknown".
- Return only valid JSON, nothing else.
"""

def encode_image_to_base64(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode('utf-8')

def validate_image_size(file_bytes: bytes):
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise ValueError(f"Image too large: {size_mb:.2f} MB (Limit: {settings.MAX_IMAGE_SIZE_MB} MB)")

def call_llm_for_analysis(base64_image: str, mime_type: str) -> dict:
    response = llm_client.chat.completions.create(
        model=settings.LLM_MODEL,
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": ANALYSIS_PROMPT
                    }
                ]
            }
        ]
    )

    raw_text = response.choices[0].message.content.strip()
    
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()
    
    return json.loads(raw_text)

async def analyze_dress_image(file: UploadFile) -> DressAnalysisResult:
    file_bytes = await file.read()
    validate_image_size(file_bytes)

    mime_type = file.content_type or "image/jpeg"
    base64_image = encode_image_to_base64(file_bytes)

    raw_json = call_llm_for_analysis(base64_image, mime_type)
    result = DressAnalysisResult(**raw_json)

    return result
        
