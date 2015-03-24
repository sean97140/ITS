.PHONY: init clean run test coverage

.DEFAULT_GOAL := run

PROJECT_NAME = its
VENV_DIR ?= .env
export PATH:=.env/bin:$(PATH):/usr/pgsql-9.3/bin:/usr/pgsql-9.1/bin
MANAGE = ./manage.py
OK_COLOR=\x1b[32;01m
NO_COLOR=\x1b[0m

# completely wipes out the database and environment and rebuilds it and loads some dummy data
init:
	rm -rf $(VENV_DIR)
	@$(MAKE) $(VENV_DIR)
	dropdb --if-exists $(PROJECT_NAME)
	createdb $(PROJECT_NAME)
	@$(MAKE) reload
	$(MANAGE) loaddata actions.json
	$(MANAGE) loaddata category.json
	@$(MANAGE) createadmin
	@$(MAKE) run



# run all the usual Django stuff to get this project bootstrapped
reload: $(VENV_DIR)
	$(MANAGE) migrate
	$(MANAGE) collectstatic --noinput
	touch $(PROJECT_NAME)/wsgi.py


# build the virtualenv
$(VENV_DIR): requirements.txt
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "Directory exists: $(VENV_DIR)"; \
		exit 1; \
	fi
	python3 -m venv $(VENV_DIR)
	curl https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py | python3
	pip install -r requirements.txt


# remove pyc junk
clean:
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete


# run the django web server
host ?= 0.0.0.0
port ?= 8000
run: $(VENV_DIR)
	$(MANAGE) runserver $(host):$(port)


# run the unit tests
# use `make test test=path.to.test` if you want to run a specific test
test: $(VENV_DIR)
	$(MANAGE) test $(test)


# run the unit tests with coverage.
# go to `0.0.0.0:8000/htmlcov/index.html` to view test coverage
coverage: $(VENV_DIR)
	coverage run ./manage.py test $(test)
	coverage html --omit=.env/*