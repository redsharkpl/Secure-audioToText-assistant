.PHONY: install run run-mcp run-ui run-all test clean check-security

install:
	uv pip install -e .

run:
	python main.py

run-ui:
	uv run streamlit run ui.py

run-mcp:
	.venv\Scripts\python mcp_server.py

run-all:
	start /B .venv\Scripts\python mcp_server.py && timeout /t 3 /nobreak && .venv\Scripts\python -m streamlit run ui.py

check-security:
	python check_secrets.py

test:
	pytest tests/

clean:
	rm -rf .venv
	rm -rf _venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .streamlit/cache
	rm -f *.mp3 *.wav *.mp4 *.png *.jpg *.jpeg test_security.txt
