
.PHONY: test
test:
	@python setup.py test

.PHONY: register
register:
	@python setup.py register

.PHONY: upload
upload:
	@python setup.py sdist upload

