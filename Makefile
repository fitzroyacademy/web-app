check:
	black --check routes app.py config.py datamodels utils
	nosetests --with-coverage --cover-package=datamodels,routes --cover-html --cover-html-dir=coverreport --cover-xml
	flake8 $(git diff --cached --name-only | grep "\.py$" | tr "\n" " ")

format:
	black routes app.py config.py datamodels utils
