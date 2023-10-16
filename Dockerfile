FROM python:3.10

WORKDIR /routing_webhook

ADD . /routing_webhook

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]