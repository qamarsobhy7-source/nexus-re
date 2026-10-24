.PHONY: install test lint doctor run docker clean

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	python -m unittest tests.test_tools -v

lint:
	flake8 nexus_re_v3.py doctor.py --max-line-length=120
	black --check nexus_re_v3.py doctor.py

doctor:
	python doctor.py

run:
	python nexus_re_v3.py

docker:
	docker build -t nexus-re:latest .

clean:
	rm -rf __pycache__ .pytest_cache
