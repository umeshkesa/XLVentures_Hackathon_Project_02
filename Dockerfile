FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system adip && adduser --system --ingroup adip adip

COPY pyproject.toml README.md ./
COPY backend ./backend
RUN pip install --upgrade pip && pip install . \
 && mkdir -p /app/logs && chown -R adip:adip /app/logs

USER adip
EXPOSE 8000

CMD ["uvicorn", "adip.main:app", "--host", "0.0.0.0", "--port", "8000"]

