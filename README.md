# KAS

## Docker based development environment

| container | description | port |
|----------|--------------|------|
|kas-web   | Container running the kas django project | 8000/tcp |
|postgres  | Postgresql container, shared between kas and selvbetjening | 5432/tcp |
|oneshot   | Container to generate and execute migrations, and unit tests |
|selvbetjening | Container running the self-service django project. | 8080/tcp |

All django containers are using gunicorn and is configured to serve static content in the development environment and
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

#worker POC
open: http://localhost:8000/worker/
press a button, see stuff works

# Working with the eSkat integration

By default a development environment does not have the neccessary information to connect to the eSkat database.
In order to connect an SSH tunnel must be created that allows accessing the database server and login and password
credentials must be provided.

The ssh tunnel can be created from the development host with the following command:

```
ssh -g -L16523:10.240.79.23:16523 magenta@10.240.76.91
```

The password needed to for the SSH connection can be found in Bitwarden under the key `magenta @ 10.240.76.91 / nopitusec04`.

Once the SSH tunnel is created a login and password is needed. These should be set up in a `docker-compose.override.yml` dockerFiles
like this:

```yaml
version: "3.4"
services:
  kas-web:
    environment:
      - ESKAT_USER=username
      - ESKAT_PASSWORD=password
```

The username and password to use can be found in BitWarden under the key `KAS login til eSkat database (10.240.79.23)`.

This will allow using the `Eskat*` model classes to connect to and query the live eSkat database.
