# Commands
.PHONY: test


# You should be under conda environment three-gen-prompt-receiver
test:
	@echo "Tests are running in the foreground."
	pytest -v tests/unit

start:
	PYTHONPATH=. pm2 start receiver.config.js

logs:
	PYTHONPATH=. pm2 logs prompts_receiver

stop:
	PYTHONPATH=. pm2 stop prompts_receiver
