URL: https://github.com/Vadeux/Async_API_sprint_1

Also contains tests from 5th sprint!

We run multiple Uvicorn instances to handle a large number of simultaneous connections.
To specify the exact number of instances:
1. Adjust the `upstream film-apis` directive in `nginx_configs/site.conf` to reflect the desired number.
2. Run the project with `docker compose up -d --scale film-api={number_of_uvicorns}`.

Run tests: cd to `film_api/tests/functional` then `docker compose up -d`
To observe test results, use `docker compose logs tests -f`
We utilize the `pytest-watch` package to automatically rerun tests whenever changes are detected
Build deps if necessary