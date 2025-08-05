FROM python:3.13-slim
LABEL authors="user"

WORKDIR /wallet_app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x wait-for-it.sh
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]