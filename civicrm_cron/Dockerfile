FROM python:3.7-stretch
RUN pip install pipenv
WORKDIR /scheduler
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy
COPY scheduler.py ./
ENTRYPOINT ["pipenv", "run", "python", "scheduler.py"]
