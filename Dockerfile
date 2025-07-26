FROM python:3.11.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

WORKDIR /app/src

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



