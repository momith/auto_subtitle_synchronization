FROM nucypher/rust-python:3.12.0

WORKDIR /app

# Copy daemon script into the container
COPY subtitle_synchronizer.py .

# For some reason root permissions required
USER root

# Install ffmpeg with a workaround (apt-get does not work directly because this container image is deprecated)
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list \
 && apt-get update -o Acquire::Check-Valid-Until=false \
 && apt-get install -y ffmpeg \
 && rm -rf /var/lib/apt/lists/*

#WORKDIR /data
WORKDIR /app/alass

# Compile alass via Rust
RUN rm -rf ./*  # Remove old files
RUN git clone https://github.com/kaegi/alass.git . \
 && cargo build --release -p alass-cli \
 && cp target/release/alass-cli /usr/local/bin/alass

# Run daemon via Python
ENTRYPOINT ["python", "-u", "/app/subtitle_synchronizer.py"]
