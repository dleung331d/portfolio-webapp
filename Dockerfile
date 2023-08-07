
FROM python:3.11.4-slim-bookworm
# install mysqlclient dependencies
RUN apt-get update && apt-get install -y --no-install-recommends pkg-config python3-dev default-libmysqlclient-dev build-essential

WORKDIR /usr/src/app
ENV FLASK_DEBUG=1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
#Server will reload itself on file changes if in dev mode
ENV FLASK_ENV=development 

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY .env .
COPY templates templates
COPY app.py .
CMD ["flask", "run"]
