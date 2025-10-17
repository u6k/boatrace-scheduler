FROM python:3.13-slim
LABEL maintainer="u6k.apps@gmail.com"

# Install softwares
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# # Install Docker CLI 
# RUN apt-get install -y --no-install-recommends ca-certificates && \
#     install -m 0755 -d /etc/apt/keyrings && \
#     curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
#     chmod a+r /etc/apt/keyrings/docker.asc && \
#     echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
#     apt-get update && \
#     apt-get install -y --no-install-recommends docker-ce-cli && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

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
