# KAS
documentation moved to: https://gronlandsprojekter.docs.magenta.dk/gl.docs.magenta.dk/projekter/kas/index.html

# Running the tests
You can run the tests with 

```
docker exec kas bash -c 'coverage run manage.py test --parallel 4 ; coverage combine ; coverage report --show-missing'
```
