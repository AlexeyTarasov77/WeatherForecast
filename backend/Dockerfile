FROM python:3.12-slim

WORKDIR /app

ENV POETRY_HOME=/opt/poetry
ENV PATH=${POETRY_HOME}/bin:${PATH}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

COPY poetry.lock pyproject.toml ./

RUN pip install poetry && pip install gunicorn

RUN poetry config virtualenvs.in-project true

RUN poetry install --no-root --no-dev 

COPY . .

EXPOSE 8000

RUN adduser --disabled-password weather_forecast

RUN chown -R weather_forecast ./weather_forecast

USER weather_forecast

WORKDIR /app/weather_forecast

ENTRYPOINT [ "poetry", "run" ]

CMD [ "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000" ]