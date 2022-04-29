FROM python:3.9-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE IoX_Coding_Innovation.settings

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

RUN pip install virtualenv

RUN mkdir /code
WORKDIR /code
RUN pip install --upgrade pip
COPY Pipfile /code/
COPY Pipfile.lock /code/

RUN pipenv install
COPY . /code/

EXPOSE 8000

CMD ["pipenv","run","python", "manage.py", "runserver", "0.0.0.0:8000"]