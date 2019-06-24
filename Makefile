install-requirements: ./Pipfile
	pipenv install
	pipenv lock -r > requirements.txt

build: install-requirements ./*
	docker build -t fitzroy-academy .

run: build
	docker run -p 5000:5000 fitzroy-academy