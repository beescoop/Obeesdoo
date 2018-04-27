# Install odoo on macos

> Tested on macos High Sierra (10.13.3)

##### 1) install Homebrew

```
$ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

##### 2) Install Python, postgresql and needed modules

```
$ brew update
$ brew install python
$ brew install postgresql
$ brew install freetype jpeg libpng libtiff webp xz
```

##### 3) Add postgresql to system startup

```
$ ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents
$ launchctl load ~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist
```
##### 4) install less compiler

```
$ brew install npm
$ npm install -g less
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
```

You should now be able to start a simple odoo instance with `python odoo.py`

## Configuring pycharm

## Troubleshoot

Missing codaparserexception

```
pip install pycoda
```

Can't update `product_scale_log` table (I did not write down the exact error)

```
truncate table product_scale_log
```

## Source
source: [setup-odoo-development-on-os-x-with-pycharm](http://bloopark.de/en_US/blog/the-bloopark-times-english-2/post/setup-odoo-development-on-os-x-with-pycharm-109)
