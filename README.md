# Cloth Image Classifier & Color Detector

A FastAPI microservice that analyzes garment images using multimodal Large Language Models (LLM Vision) to extract structured fashion attributes such as garment type, gender classification, colors, patterns, and brand identification.

---

## Features

- **Garment Classification**: Identifies clothing categories (e.g., T-shirt, shirt, pants, palazzo, jeans, saree, kurti, dress, skirt, jacket, etc.).
- **Gender Categorization**: Classifies whether the garment is targeted for male, female, or unisex.
- **Color & Pattern Detection**: Detects primary color, secondary colors, and pattern types (solid, striped, checked, floral, printed, polka-dot, abstract, etc.).
- **Brand & Logo Recognition**:
  - Detects brand names directly from visible logos with confidence scores (`high`, `medium`).
  - Fallback inference: Estimates plausible brand affiliations based on cut, style, and fabric when no logo is explicitly visible.
- **Provider-Agnostic LLM Integration**: Built on top of OpenAI SDK and compatible with any OpenAI-compatible vision endpoint (e.g., OpenAI, OpenRouter, Groq, local models via Ollama/vLLM).
- **Fast & Interactive API Documentation**: Interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) powered by FastAPI.

---

## Project Structure

```text
dress-analyzer/
├── .env.example          # Sample environment configuration
├── config.py             # Environment configuration and validation
├── llm_client.py         # LLM client initialization (OpenAI-compatible)
├── main.py               # FastAPI entry point & health check
├── requirements.txt      # Python package dependencies
├── router.py             # API route handlers (/api/v1/analyze-dress)
├── schemas.py            # Pydantic request and response schemas
└── service.py            # Image processing, prompt logic & LLM invocation
```

---

## Prerequisites

- **Python**: Version 3.10 or higher
- **Vision-capable LLM API Key**: OpenAI API key (e.g., `gpt-4o` or `gpt-4o-mini`) or compatible multimodal endpoint

---

## Installation & Setup

### 1. Clone the Repository & Navigate to Directory

```bash
git clone https://github.com/Tareq905/cloth-image-color-detector.git
cd cloth-image-color-detector
```

*(Or navigate to `dress-analyzer` if working in a monorepo workspace).*

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `dress-analyzer` directory by copying `.env.example`:

**On Windows:**
```powershell
copy .env.example .env
```

**On macOS / Linux:**
```bash
cp .env.example .env
```

Open `.env` and configure the following variables:

```env
# Required: API key for your LLM provider
LLM_API_KEY=your_api_key_here

# Required: Vision model name (e.g., gpt-4o, gpt-4o-mini)
LLM_MODEL=gpt-4o

# Optional: Custom OpenAI-compatible base URL (leave empty for OpenAI)
# LLM_BASE_URL=https://api.openai.com/v1

# Optional: Maximum allowed image size in MB (default: 5)
MAX_IMAGE_SIZE_MB=5
```

---

## Running the Application

Start the development server using Uvicorn:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access:
- **API Root / Health Check**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Alternative Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Reference

### 1. Health Check

- **Endpoint**: `GET /`
- **Description**: Returns the operational status of the service.
- **Sample Response**:
  ```json
  {
    "status": "ok",
    "service": "dress-analyzer"
  }
  ```

---

### 2. Analyze Garment Image

- **Endpoint**: `POST /api/v1/analyze-dress`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` *(required)*: Garment image file (JPEG, PNG, WEBP, etc.)

#### Example Request (`curl`)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze-dress" \
  -H "accept: application/json" \
  -F "file=@/path/to/garment.jpg"
```

#### Example Request (Python `requests`)

```python
import requests

url = "http://127.0.0.1:8000/api/v1/analyze-dress"
file_path = "sample_dress.jpg"

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "image/jpeg")}
    response = requests.post(url, files=files)

print(response.json())
```

#### Successful Response (`200 OK`)

```json
{
  "success": true,
  "filename": "sample_dress.jpg",
  "analysis": {
    "garment_type": "dress",
    "gender": "female",
    "primary_color": "navy blue",
    "secondary_colors": ["white", "gold"],
    "pattern": "floral",
    "brand": {
      "name": "Zara",
      "detected_from_logo": false,
      "confidence": "assumed"
    },
    "notes": "Brand inferred based on contemporary cut and floral pattern styling."
  },
  "error": null
}
```

#### Error Response

```json
{
  "success": false,
  "filename": "sample_dress.jpg",
  "analysis": null,
  "error": "Image too large: 6.50 MB (Limit: 5 MB)"
}
```

---

## Response Schema Details

| Field | Type | Description |
|---|---|---|
| `success` | `boolean` | Indicates whether the image was successfully analyzed. |
| `filename` | `string` | The original uploaded file name. |
| `analysis.garment_type` | `string` | Categorized garment type (e.g., `tshirt`, `shirt`, `pant`, `plazoo`, `jeans`, `saree`, `kurti`, `dress`, `skirt`, `jacket`, `other`). |
| `analysis.gender` | `string` | Target audience: `male`, `female`, or `unisex`. |
| `analysis.primary_color` | `string` | Dominant color detected on the garment. |
| `analysis.secondary_colors` | `list[string]` | Additional accents or secondary colors. |
| `analysis.pattern` | `string` | Fabric pattern (e.g., `solid`, `striped`, `checked`, `floral`, `printed`, `polka-dot`, `abstract`, `other`). |
| `analysis.brand.name` | `string` | Detected brand or best plausible inferred brand. |
| `analysis.brand.detected_from_logo` | `boolean` | `true` if identified via visible logo/tag, `false` if inferred. |
| `analysis.brand.confidence` | `string` | `high`, `medium`, `low`, or `assumed`. |
| `analysis.notes` | `string | null` | Contextual notes detailing assumptions or observations. |
| `error` | `string | null` | Error description if `success` is `false`. |

---

## License

This project is licensed under the MIT License.
