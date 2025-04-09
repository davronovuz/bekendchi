FROM python:3.11-slim

WORKDIR /app

# Install wheel first
RUN pip install --no-cache-dir wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Statik fayllarni to‘plash
RUN python manage.py collectstatic --noinput --clear

# Entrypoint skriptini qo‘shish
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Entrypoint orqali ishga tushirish
ENTRYPOINT ["/app/entrypoint.sh"]