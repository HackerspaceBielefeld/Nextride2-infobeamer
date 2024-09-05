# Use an official Python runtime as a parent image
FROM python:3.12.5-slim-bookworm

# Set environment variables to improve Python's behavior in Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group to run the app
RUN groupadd --system cms && useradd --system --gid cms cms

# Set the working directory
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip3 install --upgrade pip && pip install --no-cache-dir uwsgi

# Copy the rest of the application code
COPY . .

# Change ownership of the application directory to the non-root user
RUN chown -R cms:cms /app

# Switch to the non-root user
USER cms

# Expose the port that the app runs on
EXPOSE 5000

# Define the health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start the application using uWSGI
CMD ["uwsgi", "--ini", "uwsgi.ini"]
