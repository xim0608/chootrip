FROM xim0608/graduation_research:feature_multi_db_mysql_and_mongo

RUN mkdir /app

COPY ./Pipfile /app
COPY ./Pipfile.lock /app
WORKDIR /app

RUN pipenv install --system --deploy --ignore-pipfile

CMD ["python", "main.py"]
