FROM python:3.14-rc-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-lock.txt .
RUN pip3 install --no-cache-dir -r requirements-lock.txt

COPY . .

RUN python scripts/download_ebird.py && \
    python scripts/build_database.py && \
    rm -rf data/ebird/

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
