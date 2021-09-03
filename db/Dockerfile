FROM postgres
ENV POSTGRES_DB aiopg
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_USER=aiopg
COPY schema.sql /docker-entrypoint-initdb.d/
