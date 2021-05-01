FROM nikolaik/python-nodejs:python3.8-nodejs16

COPY . /app
RUN pip3 install -r /app/requirements.txt

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
