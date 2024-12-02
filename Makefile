.PHONY: setup dev test clean

setup:
	chmod +x setup.sh
	./setup.sh

dev:
	chmod +x dev.sh
	./dev.sh

test:
	cd backend && pytest
	cd frontend && npm test

clean:
	rm -rf backend/venv
	rm -rf frontend/node_modules
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} + 