FROM python:3.13-slim
LABEL maintainer="u6k.apps@gmail.com"

# Install softwares
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/

# Install poetry packages
WORKDIR /var/myapp
VOLUME /var/myapp

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Settings
ENV PYDEVD_DISABLE_FILE_VALIDATION=1

CMD ["poetry", "run", "python", "-m", "boatrace_scheduler"]
