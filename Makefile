build-static:
	sass static/assets/scss/fit.scss static/css/fit.css

build: ./Pipfile ./static/assets/scss/fit.scss build-static
	pipenv update
	pipenv lock -r > requirements.txt
	pipenv lock -r -d > requirements-dev.txt
	cat requirements-dev.txt | sed '1d' >> requirements.txt
	
run: build
	docker-compose build
	docker-compose up

watch: build-static
	pipenv install
	FLASK_ENV='development' pipenv run python app.py

kill:
	docker-compose down
	docker kill `docker ps -q`