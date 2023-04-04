FROM python:3.10

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["python3", "/app/main.py"]