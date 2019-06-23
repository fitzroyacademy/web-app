FROM python:3.7.3

WORKDIR /usr/local/src/

COPY ./ ./

RUN pip install -r ./requirements.txt 

RUN python reseed.py

RUN ls -al *.sqlite

EXPOSE 5000
CMD python app.py