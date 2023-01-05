### API for YaMDb
[![Django-app workflow](https://github.com/zhannaven/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)](https://github.com/zhannaven/yamdb_final/actions/workflows/yamdb_workflow.yml)
### Description
 - The main goal of the group project is to write a backend (reviews application) and an API for it (api application).
 - The YaMDb project collects reviews (Review) on compositions (Titles).
  - Compositions are divided into categories: "Books", "Films", "Music".
 - The list of categories can be expanded (for example, you can add the category "Fine Arts" or "Jewellery").
> - The works are not stored in YaMDb, you can’t watch a movie or listen to a song here.
> - A work can be assigned a genre from the predefined list (for example, Fairy Tale, Rock or Arthouse). New genres can only be created by the administrator.
> - Users can leave a comment on the composition and rate it (score in the range from one to ten). The average rating of the composition is automatically calculated.

You can read the documentation for the implemented API at [/redoc]

### Used frameworks and libraries:
- Python 3.7
- Django 2.2.16
- DRF 3.12.4
- JWT
- PostreSQL
- Nginx
- gunicorn
- Docker
- DockerHub
- GitHub Actions (CI/CD)

### Template description of .env
 - DB_ENGINE=django.db.backends.postgresql
 - DB_NAME=postgres
 - POSTGRES_USER=postgres
 - POSTGRES_PASSWORD=postgres
 - DB_HOST=db
 - DB_PORT=5432
 - SECRET_KEY=<секретный ключ проекта Django>

### How to start a project (в Unix) 
- Clone repository:

```bash
git clone git@github.com:ZhannaVen/yamdb_final.git
```
- Log in to a remote server
- Install docker on the server:
```bash
sudo apt install docker.io 
```
- Install docker-compose on the server:
```bash
curl -SL https://github.com/docker/compose/releases/download/v2.14.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```
- Edit file locally infra/nginx.conf, be sure to enter the server's IP address in the server_name line
- Copy the docker-compose.yml and nginx.conf files from the infra directory to the server:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
- Create .env according to the template above. Be sure to change the POSTGRES_USER and POSTGRES_PASSWORD values
- To work with Workflow, add environment variables to Secrets GitHub for work:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<postgres database name>
    DB_USER=<database user>
    DB_PASSWORD=<password>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<password from DockerHub>
    DOCKER_USERNAME=<username on DockerHub>
    
    SECRET_KEY=<Django project secret key>

    USER=<username to connect to the server>
    HOST=<IP of the server>
    PASSPHRASE=<password for the server, if set>
    SSH_KEY=<your SSH key (command: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID of the chat where the message will be sent>
    TELEGRAM_TOKEN=<тyour bot token>
    ```
    Four steps of Workflow:
     - Checking code for PEP8 compliance;
     - building and delivering a docker image for the web container on Docker Hub;
     - Automatic deployment to a remote server;
     - Sending a notification to a telegram chat.

- build and run containers on the server:
```bash
docker-compose up -d --build
```
- After a successful build, perform the following steps (only for the first deployment):
    * run migrations inside containers:
    ```bash
    docker-compose exec web python manage.py migrate
    ```
    * collect statics:
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```  
    * Create a Django superuser, after prompting from the terminal, enter the username and password for the superuser:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

### Filling the database
- Fill the database with data
- Back up your data:
```bash
docker-compose exec web python manage.py dumpdata > fixtures.json
```
- Stop and remove unused elements of the Docker infrastructure:
```bash
docker-compose down -v --remove-orphans
```

### User roles

- Anonymous - can view descriptions of works, read reviews and comments.
- Authenticated user (user) - can, like Anonymous, read everything, in addition, can publish reviews and rate works (films / books / songs), can comment on other people's reviews; can edit and delete his own reviews and comments. This role is assigned by default to every new user.
- Moderator (moderator) - has the same rights as the Authenticated user plus the right to remove any reviews and comments.
- Administrator (admin) - has full rights to manage all project content. Admin can create and delete works, categories and genres. Can assign roles to users.
- Django Superuser - has administrator rights (admin)

## The project was made as part of the educational process of the Python developer specialization

Participants:
- [Dmitriy - teamlead](https://github.com/vdycoder)
- [Zhanna - developer](https://github.com/ZhannaVen)
- [Luibov - developer](https://github.com/Lakrica22)

### My tasks

- Models, views and endpoints for: works, categories, genres;
- Implementing data import from csv;
- Works rating;
- ДОПИСАТЬ ПРО ДОКЕР ФАЙЛ, ACTIONS!!!