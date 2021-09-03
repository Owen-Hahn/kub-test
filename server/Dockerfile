FROM python

RUN mkdir -p /opt/server
WORKDIR /opt/server

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY server.py .

ENV DB_HOST=127.0.0.1

CMD python3 server.py --db-host $DB_HOST
