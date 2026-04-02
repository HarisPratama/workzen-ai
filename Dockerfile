# Stage 1: Build dependencies and generate gRPC stubs
FROM python:3.13-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto and generate stubs
COPY proto/ ./proto/
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/ai.proto

# Stage 2: Final lightweight image
FROM python:3.13-slim

WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy dependencies and source from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder --chown=appuser:appuser /build/proto ./proto
COPY --from=builder --chown=appuser:appuser /build/ai_pb2.py /build/ai_pb2_grpc.py ./app/
COPY --chown=appuser:appuser . .

USER appuser

# Expose REST (8000) and gRPC (50051)
EXPOSE 8000 50051

# Command to run the dual-mode service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
