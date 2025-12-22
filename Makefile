MAKEFLAGS += --silent

export DOCKER_DEFAULT_PLATFORM=linux/amd64

OPTIONS ?= --build --remove-orphans #--force-recreate
APP ?= ckan

.PHONY: docker patch healthcheck local sync test clean

docker: patch
	docker-compose up $(OPTIONS) -d

patch:
	git checkout .env.example
	patch -p1 < patch.env
	cp -f .env.example .env
	git checkout .env.example

%:
	docker-compose up $(OPTIONS) $@ -d
	docker-compose ps -a

healthcheck:
	docker inspect $(APP) --format "{{ (index (.State.Health.Log) 0).Output }}"

stats:
	docker stats --no-stream

test: docker
	PYTHONPATH=. uv run pytest --verbose

clean:
	docker-compose down --remove-orphans -v --rmi local

-include .env
