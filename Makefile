build:
	pipenv install
	pipenv lock -r > requirements.txt
	docker build -t fitzroy-academy .