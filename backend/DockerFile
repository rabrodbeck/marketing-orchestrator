# Use the official pre-configured CubeJS image as our base (based on Debian Node)
FROM cubejs/cube:v0.35.0

# Switch to root user to install python and system tools
USER root

# Install Python 3, pip, and other system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /cube/conf

# Copy backend files into the CubeJS configuration folder (/cube/conf)
COPY . /cube/conf

# Install Python package dependencies globally in the container
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# Make our startup entrypoint script executable
RUN chmod +x /cube/conf/start.sh

# Expose port 7860 (Hugging Face public standard) and 4000 (private local CubeJS)
EXPOSE 7860
EXPOSE 4000

# Set entrypoint to run both CubeJS and FastAPI
ENTRYPOINT ["/cube/conf/start.sh"]