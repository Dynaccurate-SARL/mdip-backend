FROM python:3.11

# Coping only the necessary files
#  - migrations
ADD ./alembic /src/alembic
ADD ./alembic.ini /src/alembic.ini
ADD ./entrypoint.sh /src/entrypoint.sh
#  - app
ADD ./app /src/app
ADD ./poetry.lock /src/poetry.lock
ADD ./pyproject.toml /src/pyproject.toml

WORKDIR /src
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
ENV ENV=prod
RUN pip install --upgrade pip setuptools wheel
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
EXPOSE 8000
ENTRYPOINT [ "/bin/bash", "entrypoint.sh" ]