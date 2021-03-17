FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /notification/
COPY requirements.txt /notification/requirements.txt
RUN pip install -r requirements.txt
COPY . /notification/
EXPOSE 5001
