FROM python:3.11-slim

WORKDIR /app

# Build tools va kerakli kutubxonalar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# pip, setuptools, wheel ni birga yangilaymiz
RUN pip install --upgrade pip setuptools wheel

# requirements.txt bo‘yicha install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# loyihani ko‘chirish
COPY . .

# static fayllar
RUN python manage.py collectstatic --noinput --clear

# entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
