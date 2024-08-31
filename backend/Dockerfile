FROM python:3.12-slim

WORKDIR /app

ENV POETRY_HOME=/opt/poetry \
    PATH=${POETRY_HOME}/bin:${PATH} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \ 
    POETRY_VIRTUALENVS_CREATE=false

COPY poetry.lock pyproject.toml ./

RUN pip install poetry && pip install gunicorn

RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev 

COPY . .

EXPOSE 8000

RUN adduser --disabled-password weather_forecast

RUN chown -R weather_forecast ./weather_forecast

USER weather_forecast

RUN chmod 777 /app/weather_forecast/entrypoint.sh

WORKDIR /app/weather_forecast

ENTRYPOINT [ "poetry", "run" ]

CMD ["/bin/sh", "/app/weather_forecast/entrypoint.sh"]