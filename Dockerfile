FROM python:3.7.3
RUN pip install pipenv
ADD Pipfile.lock /app/
ADD Pipfile /app/
WORKDIR /app
RUN pipenv install --deploy --system
COPY ./ /app
EXPOSE 5000
CMD ["python3", "/app/app.py"]