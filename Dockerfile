FROM python:3.9-slim
WORKDIR /app
COPY req.txt req.txt
COPY . .
RUN pip install --no-cache-dir -r req.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]