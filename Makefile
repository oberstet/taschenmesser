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

flake8:
	flake8 --ignore=E111,E114,E251,E265,E266,E303,E401,E501 taschenmesser
#	flake8 --ignore=E402,E501,E722,E741,N801,N802,N803,N805,N806 autobahn
