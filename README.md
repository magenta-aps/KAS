# KAS

## Docker based development environment

| container | description | port |
|----------|--------------|------|
|kas-web   | Container running the kas django project | 8000/tcp |
|postgres  | Postgresql container, shared between kas and selvbetjening | 5432/tcp |
|oneshot   | Container to generate and execute migrations, and unit tests |
|redis | Is qused as a Queue for the job system | 6379/tcp |

All django containers are using gunicorn and is configured to serve static content in the development environment and
log everything to stdout/stderr, so you can check the logs using docker logs <container_name>.
Gunicorn is set to auto-realod on (python) code changes in docker-compose.yml.

### Running the containers as you
Because we specify a hardcoded user and group i the docker file this causes issues when you are trying to generate
migrations and translations since the container is trying to write as an unknown user to the hosts filesystem.
To overcome this we can ask the container to run as your user since your user should be the owner of the source code
for the project and should be able to write files to the mounted volumes. Because the local user aka your UID and GID
will be different from installation to installation we can create a docker-compose.override.yml with the current
uid and gid. First obtain the UID and GID by using the id command which should output something like
```bash
uid=1000(mac) gid=1000(mac) groups=1000(mac) ....
```

Then we can crate a docker-compose.override.yml with the following content (using the obtained uid, gid).
```yaml
version: "3.4"
services:
  kas-web:
    user: "1000:1000" #uid:gid


  selvbetjening:
    user: "1000:1000"
```





### settings
All configurable settings needs to be injected using environment variables beucase we want to re-use the same
dockerFiles for development and production, if a needed setting is not provided the container should Fail fast so any
mistakes can be discovered as part of the deployment. All configurable django settings are located in
dev-environment/kas.env and dev-environment/selvbetjening.env and can be overriden directly in docker-compose.yml
using the environment block.

### Running the project
```bash
docker-compose up
```
#### container initialization
When the kas-web containter starts it by default will create the database, 
make migrations. execute migrations, create users, generate mock data and finally execute tests.  

This behavior is controlled by the following environment flags you can change in docker-compose.yml 
or add to a override if needed:

| variable | description | default |
|----------|--------------|------|
|MAKE_MIGRATIONS | Create new migrations when models change| true| 
|MIGRATE | execute all outstanding migrations| true|
|DUMMYDATA | create mock/dummy data for eskat mandtal, r75 etc| true|
|CREATE_USERS | create rest user so the selfservice container kan talk to the kas-web container| true|
|CREATE_DUMMY_USERS| create admin user with admin as the password| true|
|TEST | execute python test when starting kas-web container| true|

If you add/change/remove a dependency from a requirements.txt you have to rebuild to image using:
```bash
docker-compose build
```

### Importing eskat mock data
By default the eSkat setup will use local mockup tables as a data source for eSkat data. These tables will automatically
be used instead of the ones in the eSkat database when importing data. The tables can be populated with mockup data
by running the `python manage.py import_eskat_mockup_data` command (as done when the container starts when DUMMYDATA=true).

## Deployment
Each kas system (test/prod) kan be deployed using saltstack. you can even trigger a deployment to test from the gitlab
pipeline as a manual job after the image is release. This will clear the database and run through all migrations create 
test users etc and mock data.

To bump the currently deployed version of kas in production. You need to change the following pillar data in
the salt-automation repo `salt.pillar.customers.groenland.skat.kas.prod.sls` and create an MR:
    
    KAS_DOCKER_IMAGE: magentaaps/kas:1.3.1-kas
    KAS_SELF_DOCKER_IMAGE: magentaaps/kas:1.3.1-self

The image versions should match without the suffix (-kas/-self).
After the MR is merged the new pillar data is automatically distributed to the salt-masters and we should now be able 
to run the orchestration.

For production you need to ssh into the salt master (saltmaster-prod(ctrl1)) and access the salt-master container
and run the orchestrations. (currently kas is not using an idempotent highstate)
    
    docker exec -ti saltmaster_master_1 /bin/bash
    salt-run state.orch kas.service-prod

Effectively the orchestration updates the docker-compose.yml (with the new image versions) located in `/opt/docker/kas/`
and issues a docker pull to fetch the new image. When the new image is downloaded the orchestration stops the running containers
and brings them all up using the new image. Everything related to static files and executing migrations is handled 
by the docker-image 

## Specific documentation
[Job system](docs/jobs.md)  
[Connection to the eSkat database](docs/eskat_database.md)
