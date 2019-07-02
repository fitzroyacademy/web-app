FROM python:3.7.3
RUN mkdir /app/
ADD requirements.txt /app/
WORKDIR /app/
RUN pip install -r requirements.txt
COPY ./ /app/
EXPOSE 5000
CMD ["python3", "/app/app.py"]