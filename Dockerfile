FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get -y install --no-install-recommends git

RUN git clone https://github.com/skatilmi/ErrorPropagation
WORKDIR /usr/src/app/ErrorPropagation
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./ErrorPropagation/app.py"]
