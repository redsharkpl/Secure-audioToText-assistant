.PHONY: install run test clean

install:
	uv pip install -e .

run:
	python app/main.py

test:
	pytest tests/

clean:
	rm -rf .venv
	rm -rf __pycache__
