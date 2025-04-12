FROM python:3.13.3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY train_model.py .
COPY data ./data
RUN mkdir -p ./model

CMD ["python", "train_model.py"]