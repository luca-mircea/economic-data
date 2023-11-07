# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# WORKDIR /app
# Install Vault from Ubuntu to retrieve secrets
#FROM ubuntu

WORKDIR /app/

# Add the Python path explicitly
#ENV PYTHONPATH "${PYTHONPATH}:/app/"
ENV PYTHONPATH=.


#RUN apt update && apt install -y --no-install-recommends gpg curl lsb-release ca-certificates openssl
#RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
#RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
#RUN apt update && apt install vlt -y --no-install-recommends
#RUN apt clean && rm -rf /var/lib/apt/lists/*
#RUN vault login
#COPY --from=build /bin/hello.sh /bin/

#RUN vlt secrets >> secret-list.txt
#RUN add-apt-repository ppa:deadsnakes/ppa
#RUN apt update
#RUN apt-get update && apt-get install -y python3.11.5 python3-distutils python3-pip python3-apt
#RUN apt install python3-pip
#ADD . .
#RUN python3.11.5 -m venv ./venv
#RUN python3.11.5 -m pip install -r requirements.txt

#WORKDIR /app

# Switch back to Python after having used Ubuntu to intall Vault
#FROM python:${PYTHON_VERSION}-slim as base

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser


# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt

# Copy the source code into the container.
COPY . /app/

# Set up Python
RUN python -m venv venv
# COPY requirements.txt .
# RUN app/venv/bin/activate
RUN pip install setuptools
RUN pip install build
RUN python -m build
#RUN pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser
# WORKDIR /app/economic-data
#CMD ["python", "-m", "exchange_rate_scraper"]
ENTRYPOINT ["python", "-m", "exchange_rate_scraper"]

# Last step: get secrets from the Vault

# Run the application.
#CMD python3 'exchange_rate_scraper.er_scraper.py:main'
#CMD ["python3.11.5","exchange_rate_scraper/main.py"]