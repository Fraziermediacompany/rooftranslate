FROM python:3.11-slim

WORKDIR /app

# System deps for pdfplumber/reportlab (none required at runtime, but helpful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY fixtures/ fixtures/

ENV ROOFTRANSLATE_MODE=fixture
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
