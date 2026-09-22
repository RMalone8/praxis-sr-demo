FROM python:3.12-alpine

WORKDIR /app
COPY server.py /app/server.py
RUN mkdir /data && chown 1001:0 /data

ENV TRACE_DB_PATH=/data/traces.db \
    PRAXIS_UPSTREAM=http://praxis:8080

EXPOSE 8080 8081 8082
VOLUME ["/data"]
USER 1001
CMD ["python", "/app/server.py"]
