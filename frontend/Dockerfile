FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy frontend files
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start Python HTTP server
CMD ["python", "-m", "http.server", "3000", "--bind", "0.0.0.0"]
