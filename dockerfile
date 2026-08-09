FROM python:3.11-slim AS base

#don't create .pyc bytecode files
ENV PYTHONDONTWRITEBYTECODE=1
#output logs immediately rather than buffering them 
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /app

USER appuser


FROM base AS api

COPY --chmod=755 docker/entrypoint.sh /entrypoint.sh

#just metadata
EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]


FROM base AS worker

CMD ["python", "-m", "worker.worker"]