FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install dependencies (cache-friendly)
COPY backend/requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend, frontend, and media
COPY backend/ backend/
COPY Frontend/ Frontend/
COPY media/ media/

# Set working directory to backend
WORKDIR /app/backend

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Gunicorn pointing to config folder
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
