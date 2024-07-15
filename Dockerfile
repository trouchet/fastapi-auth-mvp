# Use the official Python image as the base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY backend .
COPY .env .

# Command to run the FastAPI application
CMD [\
    "gunicorn", \
    "backend.app.main:app", \
    "--workers", "3", \
    "--worker-class" "uvicorn.workers.UvicornWorker", \ 
    "--host", "0.0.0.0", \
    "--port", "8001" \
]