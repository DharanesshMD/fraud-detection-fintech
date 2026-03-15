FROM python:3.11-slim
WORKDIR /app

# Install simple runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Expose API port
EXPOSE 8000

CMD ["uvicorn", "src.api.predict:app", "--host", "0.0.0.0", "--port", "8000"]
