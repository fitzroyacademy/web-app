build-static:
	sass static/assets/scss/fit.scss static/css/fit.css

install-requirements: ./Pipfile build-static
	pipenv update
	pipenv lock -r > requirements.txt
	
install-dev-requirements: ./Pipfile build-static
	pipenv update -d
	pipenv lock -r -d > requirements-dev.txt
	cat requirements-dev.txt | sed '1d' >> requirements.txt

build: install-requirements install-dev-requirements ./*
	make build-static # make sure it runs
	docker build -t fitzroy-academy .

run: build
	FLASK_ENV='development' docker run -p 5000:5000 fitzroy-academy

docker-watch: build
	FLASK_ENV='development' docker run --mount type=bind,source=`pwd`,target=/app -p 5000:5000 fitzroy-academy:latest

watch: build-static install-requirements install-dev-requirements ./*
	FLASK_ENV='development' pipenv run python app.py