FROM debian:9.5
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN apt-get update \
 && apt-get install --yes --no-install-recommends \
      libxml2-dev \
      libxslt-dev \
      python3 \
      python3-dev \
      python3-pip \
 && pip3 install pipenv
WORKDIR /usps
COPY Pipfile Pipfile.lock ./
RUN pipenv install
COPY server.py ./
ENV LOG_LEVEL=INFO
ENTRYPOINT ["/usr/local/bin/pipenv", "run", "gunicorn", \
            "--workers", "2", \
            "--bind", "0.0.0.0:80", \
            "server:APPLICATION"]
