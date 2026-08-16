FROM python:3.14-slim

# Evita che Python scriva file .pyc e forza l'output senza buffer per i log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Imposta la cartella di lavoro all'interno del container
WORKDIR /app

# Copia prima solo il file delle dipendenze (sfrutta la cache dei layer Docker)
COPY requirements.txt .

# Installa le librerie Python
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /app

# Espone la porta di default di Streamlit
EXPOSE 8501

# Comando per avviare Streamlit disabilitando il CORS e l'indirizzo headless
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]