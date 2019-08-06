FROM python:3.7-slim
RUN apt-get update
RUN apt-get install libpq-dev gcc musl-dev -y
RUN mkdir /app/
ADD requirements.txt /app/
WORKDIR /app/
RUN pip install -r requirements.txt
COPY ./ /app/
EXPOSE 5000
CMD ["python3", "-u", "/app/app.py"]