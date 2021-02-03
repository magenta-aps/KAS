# KAS

## Docker based development environment

| container | description | port |
|----------|--------------|------|
|kas-web   | Container running the kas django project | 8000/tcp |
|postgres  | Postgresql container, shared between kas and selvbetjening | 5432/tcp |
|oneshot   | Container to generate and execute migrations, and unit tests |
|selvbetjening | Container running the self-service django project. | 8080/tcp |

All django containers are using gunicorn and is confgiured to serve static in the development environment and 
log everything to stdout/stderr, so you can check the logs using docker logs <container_name>.
Gunicorn is set to auto-realod on (python) code changes.

### Running the project
```bash
docker-compose up
```

If you add/change/remove a dependency from a requirements.txt you have to rebuild to image using:
```bash
docker-compose build
```

## settings
All configurable settings needs to be injected using environment variables beucase we want to re-use the same
dockerFiles for development and production, if a needed setting is not provided the container should Fail fast so any
mistakes can be discovered as part of the deployment. All configurable django settings are located in 
dev-environment/kas.env and dev-environment/selvbetjening.env and can be overriden directly in docker-compose.yml
using the environment block.
