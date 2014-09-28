
.PHONY: test
test:
	@python setup.py test

.PHONY: register
register:
	@python setup.py register

.PHONY: upload
upload:
	@python setup.py sdist upload

.PHONY: demo
demo:
	@mkdir -p etc/buildout
	@if [ ! -e "etc/buildout/.installed.cfg" ]; then \
		echo "Bootstrapping with $$(python -c 'import sys;print(sys.executable)')"; \
		python bootstrap.py; \
	fi;
	@./bin/buildout
	@./bin/django makemigrations --noinput 2>/dev/null && ./bin/django migrate --noinput 2>/dev/null

.PHONY: invite
invite:
	@./bin/django invite --noinput --email=bob@builder.com 2>/dev/null

.PHONY: serve
serve:
	@./bin/django runserver

.PHONY: shell
shell:
	@./bin/django shell

