# This dockerfile serves as a base for all testing images.
# It contains all dependencies and is therefore bigger.
FROM python:3.11

ARG PYTHON_VERSION=3.11
ARG POETRY_VERSION=1.5.1
LABEL maintainer="RISC Software GmbH <office@risc-software.at>"

RUN pip install --upgrade pip

ENV MQTT_HOST=localhost
ENV MQTT_PORT=1883

# Install python and set interpreter
#RUN pyenv install -s ${PYTHON_VERSION} && pyenv global ${PYTHON_VERSION}

# Install and configure Poetry
ENV POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:${POETRY_HOME}/bin"

# Setup directory structure
RUN mkdir /repo
WORKDIR /repo

# Install dependencies (package itself is not installed)
COPY pyproject.toml poetry.lock .
RUN poetry install --all-extras --no-root

# Copy the rest of the repository
ADD . .

CMD [ "python", "./main_dat.py" ]