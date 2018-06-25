# Install odoo on linux

> Tested on Ubuntu 18


##### 2) Install Python, postgresql and needed modules

Python 2.7 and 3 come pre-installed  but you'll need to add pip

```
sudo apt-get install python-pip
sudo apt-get install postgresql
sudo apt-get install libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev -y
sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
```


##### 4) install less compiler

```
$ sudo apt-get install npm
$ sudo npm install -g less less-plugin-clean-css
```

##### 5) setup odoo environment

I recommend using [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/index.html)

```
$ mkvirtualenv odoo -p /path/to/python2.7  # generally /usr/bin/python2.7
$ which python  # should return:
/Users/<user>/.virtualenvs/odoo/bin/python
```
Use `deactivate` to get out of odoo environment, use `workon odoo` to activate the environment.

##### 6) clone odoo

```
$ cd ~/projects
$ git clone https://github.com/odoo/odoo.git odoo
```

##### 7) Install odoo requirements

```
$ cd odoo
$ git checkout 9.0
$ pip install -r requirements.txt

# we need to upgrade psycopg2
pip uninstall psycopg2
pip install --no-binary :all: psycopg2
```

You should now be able to start a simple odoo instance with `./odoo/odoo.py`

