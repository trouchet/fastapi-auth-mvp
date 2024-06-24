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
COPY static .
COPY .env .

# Command to run the FastAPI application
CMD [\
    "uvicorn", \
    "backend.app.main:app", "--reload", \
    "--workers", "4", \
    "--host", "0.0.0.0", \
    "--port", "8000" \
]
