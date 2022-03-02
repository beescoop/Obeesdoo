# Create development environment using docker

> Tested on fedora 31

## 1) install Docker

Checkout the [installation guide](https://docs.docker.com/install/) from docker. TODO:
make it work with [podman](https://podman.io/).

Be sure to start the docker daemon using `systemctl start docker` (enable if you want it
to persist on reboot). Depending on the distribution, you might need to either use sudo
or create a docker group. The following instructions assume that you can use docker
without being root, add sudo if necessary.

## 2) Build the images (odoo - postgresql)

~ 15 minutes

```bash
docker-compose build
```

## 3) Load data in postgresql

Copy the sql.gz dump into the `initial-data-load` folder. Prefix it with 02, so that it
is loaded after user creation and before the crons are stopped.

```bash
docker-compose up db
```

This could take a while (~20 minutes) depending on the data dump you are using. In order
to reset your database, remove the container. (It will have to rebuild the database the
next time you start it).

```bash
docker-compose rm db
```

## 4) Run the project

If you are not using a pre-created db run

```bash
docker-compose run odoo python3 odoo-bin -d beescoop -i base -c odoo.conf
```

All the modules need to be updated in order to be recognised. To do that run

```bash
docker-compose run -p 8096:8096 odoo python odoo.py -c odoo.conf -d beescoop -u all
```

Once the update has been done, you can simply run the whole project by running

```bash
docker-compose up
```

I like to start the database in the background to only have the logs of the application.

```bash
docker-compose up -d db
docker-compose up odoo
```

## 5) Login

To login you may either use your account or the admin account whose password should have
been reset to admin.
