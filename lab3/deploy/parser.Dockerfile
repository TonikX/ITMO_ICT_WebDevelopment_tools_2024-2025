FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y wget gnupg2 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 \
    libpango-1.0-0 libgtk-3-0 libxshmfence1 libxfixes3 libxext6 libx11-6 libxcb1 libx11-xcb1 \
    libxrender1 libxi6 libxtst6 libwayland-client0 libwayland-cursor0 libwayland-egl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install playwright && playwright install --with-deps

COPY . .

CMD ["uvicorn", "parser_api:app", "--host", "0.0.0.0", "--port", "8000"]