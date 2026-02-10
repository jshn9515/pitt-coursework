# Use the official Python image (stable and Gradescope-friendly)
FROM python:3.14-slim

ENV TZ=America/New_York

RUN apt-get update && apt-get install -y tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install gRPC and its tools
RUN python -m pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

# Generate Python code from the chat.proto file
RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    chat.proto

# Run the tests when the container starts
CMD ["python", "run_all_tests.py"]
