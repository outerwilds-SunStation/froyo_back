FROM python:3.9-slim

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY req.txt req.txt
COPY . .

RUN pip install --upgrade pip
RUN pip install -r req.txt

ENV PORT 8080

COPY keys/datastore-access-key.json /app/datastoreserviceAccountKey.json
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/datastoreserviceAccountKey.json"

CMD exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT}