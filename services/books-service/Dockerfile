# Stage 1: Builder/Test Stage
# This stage installs dependencies, copies all code, and could run tests.

FROM python:3.9.23-slim-bullseye AS builder_stage

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
FROM python:3.9.23-slim-bullseye AS production_stage

LABEL stage="production"

# Set the working directory inside the container
WORKDIR /app
RUN echo "--- Production Stage: Working directory set to /app ---"

# Create a non-root user and group for enhanced security
RUN addgroup --system flaskgroup && adduser --system --ingroup flaskgroup flaskuser

# Copy the installed packages and application code from the builder stage
# This efficiently brings over only what's needed for the application to run.
COPY --from=builder_stage /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder_stage /app /app
RUN echo "--- Production Stage: Copied application artifacts from builder stage ---"

# Change ownership of the /app directory to the non-root user
RUN chown -R flaskuser:flaskgroup /app

# Switch to the non-root user
USER flaskuser

# Expose the port on which the Flask application will listen
EXPOSE 5000
RUN echo "--- Production Stage: Port 5000 exposed ---"

# Add HEALTHCHECK instruction
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:5000/health || exit 1

# Define the command to run the Flask application with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
RUN echo "--- Production Stage: Command to run app.py defined ---"

