FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY ai-services /app/ai-services
COPY models /app/models

RUN pip install --no-cache-dir /app/ai-services

EXPOSE 8100

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8100"]
