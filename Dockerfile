FROM python:3.11-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# include Alembic bits so the container knows where migrations live
COPY alembic.ini .
COPY migrations ./migrations

COPY ./app ./app

CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
