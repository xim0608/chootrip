FROM xim0608/graduation_research:feature_multi_db_mysql_and_mongo

RUN wget http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/pyknp-0.3.tar.gz -O /tmp/pyknp-0.3.tar.gz &&\
    cd /tmp && pip install pyknp-0.3.tar.gz

RUN mkdir /app

COPY ./Pipfile /app
COPY ./Pipfile.lock /app
WORKDIR /app

RUN pipenv install --system --deploy --ignore-pipfile

CMD ["python", "main.py"]
