# Use the official Python image.
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app
COPY . .

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "similarity_agent:app"]