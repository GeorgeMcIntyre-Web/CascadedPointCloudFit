FROM python:3.10-slim-buster

WORKDIR /app

# Copy all files to the container
COPY . /app

# Install system dependencies required by open3d
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libx11-6 \   
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Flask and other Python dependencies
RUN pip install Flask
RUN python -m pip install --no-cache-dir -r requirementsLinux.txt

# Expose port 5000 for Flask
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]