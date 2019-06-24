FROM python:3.7.3
ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r ./requirements.txt 
COPY ./ /app
CMD python app.py