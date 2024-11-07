
FROM python:3.12-alpine


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./app /code/app

COPY .env /code/.env

EXPOSE 80

CMD ["fastapi", "run", "app/main.py", "--port", "80"]