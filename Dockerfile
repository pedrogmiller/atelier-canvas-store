FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose standard port
EXPOSE 8000

# Start production server
CMD ["uvicorn", "storefront.app:app", "--host", "0.0.0.0", "--port", "8000"]
