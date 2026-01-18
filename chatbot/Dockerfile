FROM pytorch/pytorch:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["python", "app.py"]
