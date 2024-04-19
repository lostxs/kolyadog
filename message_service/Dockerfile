ARG BASE_IMAGE=python:3.9-slim-buster
FROM $BASE_IMAGE

# system update & package install
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add a new user 'user' with a home directory, no password, and specific UID
RUN adduser --disabled-password --gecos "" --uid 1001 user

USER user

WORKDIR /app

COPY . /app

# pip & requirements with local user installation
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --user -r requirements.txt

# Execute
CMD ["python", "main.py"]