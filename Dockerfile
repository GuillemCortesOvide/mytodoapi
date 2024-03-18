# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install build-essential (includes gcc) and other necessary packages
RUN apt-get update && \
    apt-get install -y build-essential libaio1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for database location
ENV DATABASE_DIR=/data
ENV DATABASE_FILE=my_todo.db
ENV DATABASE_URL=sqlite:///$DATABASE_DIR/$DATABASE_FILE

# Ensure the directory exists
RUN mkdir -p $DATABASE_DIR

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# investigar diff entre copy y add comandos
# alojar base de datos del client por default