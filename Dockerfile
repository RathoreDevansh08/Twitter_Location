FROM nikolaik/python-nodejs:python3.8-nodejs16
EXPOSE 5000
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
COPY . /app

ENV FLASK_ENV=development
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
