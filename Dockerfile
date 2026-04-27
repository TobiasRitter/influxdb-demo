FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV INFLUX_HOST=http://influxdb3-core:8181
ENV INFLUX_DATABASE=demo

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
