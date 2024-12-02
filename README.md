1. Install Docker
2. Confirm installation: `docker run hello-world` - update user permissions as needed
3. Run `docker compose up --build -d` to start the application
4. The backend is now running at `localhost:5000`
5. To view/tail logs, run `docker compose logs -f`. To view logs for a specific service, run `docker compose logs -f <service_name>`
5. Saving files will automatically reload the server
6. Run `docker compose down` to stop the application
7. If you need to change packages available in the backend, update the `requirements.txt` file and rebuild the image (down then up)

8. Postgres setup and Troubleshooting
9. Run `docker ps` to check if your containers are up and running - you should see **tct_database** running. If not, try running `docker compose up -d`
10. Make sure you POSTGRES_PASSWORD and POSTGRES_USER are correctly configured in `.env` file or Docker Compose file
11. Run `psql -U postgres -h localhost -d tct_database`
12. Initializing Migrations for the first time? `flask db init`, `flask db migrate`, & `flask db upgrade`
13. Run `flask db upgrade` and make sure it completes without errors
