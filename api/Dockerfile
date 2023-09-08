### To minimize build time, perform steps where the contents aren't likely to change first
###
FROM python:3.11.4-slim-bookworm

ENV TZ=Canada/Pacific
# Install the timezone data package (Debian/Ubuntu)
RUN apt-get update && apt-get install -y tzdata

WORKDIR /usr/src/app
COPY fast-api-requirements.txt fast-api-requirements.txt
RUN pip install -r fast-api-requirements.txt

# Contents that are more likely to change during development
COPY fastapi-main.py .

RUN ls -la

# IMPORTANT: Remove --reload for PRODUCTION use!!!!!!!!!!!!!!!!!!!!!!!!!
# TESTING in DEBUG MODE
CMD ["uvicorn", "fastapi-main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
