.PHONY: install run dev clean

install:
	pip install -r requirements.txt

run:
	python app.py

dev: install
	FLASK_ENV=development FLASK_DEBUG=1 python app.py

clean:
	rm -f instance/database.db
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true