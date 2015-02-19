all:
	@echo "Targets:"
	@echo ""
	@echo "   install          Local install"
	@echo "   clean            Cleanup"
	@echo "   build            Clean build"
	@echo "   publish          Clean build and publish to PyPI"
	@echo ""

install:
	python setup.py install

clean:
	rm -rf ./taschenmesser.egg-info
	rm -rf ./build
	rm -rf ./dist
	find . -name "*.pyc" -exec rm -f {} \;

build: clean
	python setup.py bdist_egg

publish: clean
	python setup.py register
	python setup.py sdist upload
