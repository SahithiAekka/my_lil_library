# Stage 1: Builder/Test Stage
# This stage installs dependencies, copies all code, and could run tests.

FROM python:3.9 AS builder_stage

LABEL stage="builder"

# Set the working directory inside the container
WORKDIR /app
RUN echo "--- Builder Stage: Working directory set to /app ---"

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN echo "--- Builder Stage: Copied requirements.txt ---"

# Install dependencies
RUN echo "--- Builder Stage: Installing Python dependencies ---" && \
    pip install --no-cache-dir -r requirements.txt
RUN echo "--- Builder Stage: Dependencies installed ---"

# Copy all application code (including app.py and any test files for future external testing)
COPY . .
RUN echo "--- Builder Stage: Copied all application code ---"

# Integration tests will be run externally after deployment with Docker Compose.


# Stage 2: Production Stage
# This stage creates a lean, production-ready image.
# It copies only the necessary artifacts (installed packages, app code) from the builder stage.
FROM python:3.9-slim AS production_stage

LABEL stage="production"

# Set the working directory inside the container
WORKDIR /app
RUN echo "--- Production Stage: Working directory set to /app ---"

# Copy the installed packages and application code from the builder stage
# This efficiently brings over only what's needed for the application to run.
COPY --from=builder_stage /app /app
RUN echo "--- Production Stage: Copied application artifacts from builder stage ---"

# Expose the port on which the Flask application will listen
EXPOSE 5000
RUN echo "--- Production Stage: Port 5000 exposed ---"

# Define the command to run the Flask application when the container starts
CMD ["python", "app.py"]
RUN echo "--- Production Stage: Command to run app.py defined ---"

