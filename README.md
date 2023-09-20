# Backend IoT

## Instructions

### Debug
```
poetry install
poetry run flask --app backend_iot run --port 1111 --debug
```

### Production
```
poetry install --with prod
poetry run waitress-serve --port 1111 backend_iot:app
```
