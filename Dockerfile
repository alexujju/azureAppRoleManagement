# Use Python 3.11 Alpine as the base image
FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required system dependencies (for some Python libraries)
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the Flask port
EXPOSE 5000

# Run Flask when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
