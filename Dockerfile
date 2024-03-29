FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get -y install libpq-dev gcc curl procps net-tools tini \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install gunicorn

ENV POETRY_HOME=/tmp/poetry
RUN curl -sSL https://install.python-poetry.org/ | python3 -
ENV PATH=$POETRY_HOME/bin:$PATH
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
# copying poetry stuff before the rest of the code to take advantage of docker caching
COPY poetry.lock .
COPY pyproject.toml .

RUN poetry config virtualenvs.create false \
  && poetry install --only main

COPY . /app


EXPOSE 8000

CMD bash -c "uvicorn app.main:app --host 0.0.0.0 --port 8000"