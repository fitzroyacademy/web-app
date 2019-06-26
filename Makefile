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

kill:
	docker-compose down

purge-db:
	docker-compose down -v

connect-db:
	docker exec -it $$(docker ps -f name="postgres" -q) psql -U postgres

connect-app:
	docker exec -it $$(docker ps -f name="fitzroy-academy-app" -q) /bin/bash