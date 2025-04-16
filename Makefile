MAKEFLAGS += --silent

export DOCKER_DEFAULT_PLATFORM=linux/amd64

OPTIONS ?= --build --remove-orphans #--force-recreate
APP ?= ckan

.PHONY: docker patch healthcheck local sync test clean

docker: patch
	docker-compose up $(OPTIONS) -d

patch:
	#cp -f .env.example .env
	patch -p1 < .env.patch

%:
	docker-compose up $(OPTIONS) $@ -d
	docker-compose ps -a

healthcheck:
	docker inspect $(APP) --format "{{ (index (.State.Health.Log) 0).Output }}"

stats:
	docker stats --no-stream

test:
	PYTHONPATH=. uv run pytest --verbose

clean:
	docker-compose down --remove-orphans -v --rmi local

-include .env
