FROM ubuntu:latest	

RUN apt-get install moc -yq && apt-get install python3-pip -yp

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "run.py" ]
