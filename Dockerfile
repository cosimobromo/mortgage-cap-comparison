FROM python:3.14-slim

# Prevents Python from writing .pyc files and forces unbuffered output for logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy dependencies file first (leverages Docker layer caching)
COPY requirements.txt .

# Install Python libraries
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /app

# Expose Streamlit default port
EXPOSE 8501

# Command to start Streamlit with CORS disabled and headless address
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]