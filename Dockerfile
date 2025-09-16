# Use the official Python image as a base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/staticfiles /app/static && \
    chmod -R 755 /app/staticfiles /app/static && \
    # Install Django admin static files
    python -c "import django; print(django.__path__[0] + '/contrib/admin/static')" > /tmp/django_admin_static.txt && \
    # Copy Django admin static files
    cp -r `cat /tmp/django_admin_static.txt`/admin /app/staticfiles/ && \
    # Copy DRF static files
    python -c "import rest_framework; print(rest_framework.__path__[0] + '/static')" > /tmp/drf_static.txt && \
    cp -r `cat /tmp/drf_static.txt`/rest_framework /app/staticfiles/

# Expose the port the app runs on
EXPOSE 8050

# Command to run the application
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8050"]
