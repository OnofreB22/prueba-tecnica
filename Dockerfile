FROM python:3.13.5-alpine3.22
LABEL maintainer="oabenjumev@gmail.com"

WORKDIR /app

RUN pip install --upgrade pip

RUN apk add --no-cache postgresql-dev gcc musl-dev python3-dev

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
