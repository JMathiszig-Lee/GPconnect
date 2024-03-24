FROM python:3.10

WORKDIR /code

RUN pip install pipenv

COPY Pipfile /code/Pipfile
COPY Pipfile.lock /code/Pipfile.lock
COPY keys/test-1.pem /code/keys/test-1.pem

RUN pipenv install --system --deploy

COPY app /code/app

CMD uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-80}
