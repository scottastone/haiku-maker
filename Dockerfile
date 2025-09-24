# Use an official lightweight Python image
FROM python:3.13-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file first to leverage Docker cache
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Expose the port that the app runs on
EXPOSE 6767

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:6767", "app:app"]