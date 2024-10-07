FROM python:3.9-slim

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY req.txt req.txt
COPY . .

RUN pip install --upgrade pip
RUN pip install -r req.txt

EXPOSE 8080
ENV PORT 8080

CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "${PORT}"]