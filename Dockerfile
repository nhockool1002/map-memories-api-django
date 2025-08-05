FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies including GDAL and PostGIS
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        gettext \
        git \
        # GDAL and PostGIS dependencies
        gdal-bin \
        libgdal-dev \
        postgis \
        postgresql-15-postgis-3 \
        # Additional dependencies for GDAL
        libgeos-dev \
        libproj-dev \
        proj-bin \
        proj-data \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so
ENV PROJ_LIB=/usr/share/proj

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create static and media directories
RUN mkdir -p /app/static /app/media

# Collect static files (this will be run again in docker-compose command)
RUN python manage.py collectstatic --noinput --clear || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command (overridden in docker-compose)
CMD ["gunicorn", "map_memories.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]