FROM python:3.12-slim

RUN useradd -m -u 1000 botuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

USER botuser

CMD ["python", "-m", "app.main"]
