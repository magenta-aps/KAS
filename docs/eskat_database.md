# eSkat database

## Connecting to the real eSkat database

By default a development environment does not have the neccessary information to connect to the eSkat database.
In order to connect an SSH tunnel must be created that allows accessing the database server and login and password
credentials must be provided.

The ssh tunnel can be created from the development host with the following command:

```
ssh -g -L16523:10.240.79.23:16523 -L16524:10.240.79.20:16523 10.240.76.76
```

This will have the real database listening on localhost port 16523 and the GPS database listening on port 16524.

Once the SSH tunnel is created a login and password is needed. These should be set up in a `docker-compose.override.yml` dockerFiles
like this:

```yaml
version: "3.4"
services:
  kas-web:
    environment:
      - ESKAT_USER=username
      - ESKAT_PASSWORD=password
      - ESKAT_PORT=16524
      - ESKAT_DB=DBSERVICE_AKA_KAS_GPS
  worker:
    environment:
      - ESKAT_USER=username
      - ESKAT_PASSWORD=password
      - ESKAT_PORT=16524
      - ESKAT_DB=DBSERVICE_AKA_KAS_GPS
```

The username and password to use can be found in BitWarden under the key `KAS login til eSkat database (10.240.79.23)`.

To connect to the GPS system use the servicename `DBSERVICE_AKA_KAS_GPS`. Username and password are the same as for the
production database.

This will allow using the `eskat.models.EskatModels.*` model classes to connect to and query the live eSkat database.

If `settings.ENVIRONMENT` is set to `production`, the real eSkat database will be used by default.
