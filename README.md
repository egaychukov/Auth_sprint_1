URL: https://github.com/egaychukov/Auth_sprint_1

We run multiple Uvicorn instances to handle a large number of simultaneous connections.
To specify the exact number of instances:
1. Adjust the `upstream film-apis` directive in `nginx_configs/site.conf` to reflect the desired number.
2. Run the project with `docker compose up -d --scale film-api={number_of_uvicorns}`.

Run tests: 
1. cd to `film_api/tests/functional` or `auth/tests/functional`, then `docker compose up -d`
2. Use `docker compose logs tests -f` to observe test results
We utilize the `pytest-watch` package to automatically rerun tests whenever changes are detected

Roles & admin set-up (the order matters):
1. `docker compose exec auth python admin/admin.py roles-admin` for adding roles to the database
2. `docker compose exec auth python admin/admin.py setup-admin` for creating an initial admin user
