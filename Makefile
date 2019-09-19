check:
	black --check routes app.py config.py datamodels.py models.py util.py
	flake8 $(git diff --cached --name-only | grep "\.py$" | tr "\n" " ")
    nosetests --cover-package=routes.course,datamodels

format:
	black routes app.py config.py datamodels.py models.py util.py
