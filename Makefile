.SHELLFLAGS = -eu


.PHONY: build-docs
build-docs: README.md README.html

NOGIT=

README.xml: README.adoc
	asciidoctor --backend=docbook --doctype=article --out-file=$@ $<
	test -n '$(NOGIT)' || git add $@

README.md: README.xml
	pandoc --from=docbook --to=gfm --output=$@ $<
	test -n '$(NOGIT)' || git add $@

README.html: README.adoc
	asciidoctor --backend=html5 --doctype=article --embedded --out-file=$@ $<
	test -n '$(NOGIT)' || git add $@


.PHONY: build-python
build-python: README.md
	dev.venv/bin/python -m build
	@# Test the package
	python -m venv --clear test.venv
	test.venv/bin/pip install $$( find dist -type f -name '*.whl' | sort -i | tail -n1 )
	test.venv/bin/pph project inspect

.PHONY: publish-testpypi
publish-testpypi:
	@# Upload all to PyPI
	find dist -type f -not -name '*+g*' -print0 | \
	  xargs -0 dev.venv/bin/twine upload --repository testpypi
	@# Test the package
	python -m venv --clear test.venv
	test.venv/bin/pip install --index-url https://test.pypi.org/simple/ python-project-helper
	test.venv/bin/pph project inspect

.PHONY: publish-pypi
publish-pypi:
	@# Upload all to PyPI
	find dist -type f -not -name '*+g*' -print0 | \
	  xargs -0 dev.venv/bin/twine upload
	@# Test the package
	python -m venv --clear test.venv
	test.venv/bin/pip install --index-url https://test.pypi.org/simple/ python-project-helper
	test.venv/bin/pph project inspect


git_sourcehut = git@git.sr.ht:~wintershadows/python-project-helper
git_github = git@github.com:gwerbin/python-project-helper.git

.PHONY: setup
setup:
	git remote add all '$(git_sourcehut)'
	git remote set-url --add --push all '$(git_sourcehut)'
	git remote set-url --add --push all '$(git_github)'
	python -m venv dev.venv
	dev.venv/bin/pip install --upgrade pip wheel
	dev.venv/bin/pip install \
	  --requirement requirements-dev.in \
	  --editable '.[tests]'
