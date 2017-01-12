all:
	@echo "Targets:"
	@echo ""
	@echo "   install          Local install"
	@echo "   clean            Cleanup"
	@echo "   build            Clean build"
	@echo "   publish          Clean build and publish to PyPI"
	@echo ""

install:
	pip install --upgrade -e .

clean:
	rm -rf ./taschenmesser.egg-info
	rm -rf ./build
	rm -rf ./dist
	find . -name "*.pyc" -exec rm -f {} \;

build:
	python setup.py sdist bdist_wheel

publish: clean build
	twine upload dist/*
