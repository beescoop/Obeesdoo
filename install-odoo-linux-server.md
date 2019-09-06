# Install odoo on a linux server

> by Thibault François 

## Installation basique

##### 1) ajouter un utilisateur odoo

    # adduser odoo

##### 2) installation de postgresql (DBMS)

    # apt-get install postgresql

##### 3) install git

    # apt-get install git

##### 4) installer pip : python package manager

    # apt-get install python-pip

##### 5) installation des paquets devel pour compilation des bibliothèques python

    # apt-get install python-dev postgresql-server-dev-all libjpeg-dev zlib1g-dev libpng12-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev

##### 6) installation de node-less

    # apt-get install node-less

##### 7) clone odoo

    # su odoo
    $ cd /home/odoo
    $ git clone https://github.com/odoo/odoo.git

##### 8) installer bibliothèque python

    $ exit
    # cd /home/odoo/odoo
    # pip install -r requirements.txt

##### 9) créer odoo user pour postgresql avec les droits de création de base de donnée

    # su postgres
    $ createuser -d odoo
    $ exit

##### 10) Installer wkhtml to pdf 0.12.1 !! (pas une autre) (sur une machine 64 bit avec un ubuntu 64bit 14.04) 

    # apt-get install fontconfig  libfontconfig1 libxrender1 fontconfig-config
    # wget http://download.gna.org/wkhtmltopdf/0.12/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb
    # dpkg -i wkhtmltox-0.12.1_linux-trusty-amd64.deb
    # cd /usr/local/bin/
    # cp wkhtmltoimage /usr/bin/wkhtmltoimage
    # cp wkhtmltopdf /usr/bin/wkhtmltopdf

##### 11) Tester l'installation de odoo

    # su odoo
    $ cd /home/odoo/odoo
    $ ./odoo.py

lancer le navigateur http://localhost:8069 la page de création de base de donnée d'odoo devrait s'ouvrir, essayé de créer une base de donnée

ctrl + c pour tuer le processus odoo depuis la console

## Pour aller plus loin: init.d script

##### 1) créer un répertoire de log

    # su odoo
    $ mkdir /home/odoo/log

##### 2) créer fichier de config odoo

    $ cd /home/odoo/odoo
    $ ./odoo.py -s -c /home/odoo/odoo.conf --stop-after-init --logfile=/home/odoo/log/odoo.log

##### 3) Créer le fichier init.d

    $ exit
    $ vim /etc/init.d/odoo  

copier le contenu dans le fichier (gedit va aussi bien que vim) 


    #!/bin/sh

    ### BEGIN INIT INFO
    # Provides:             openerp-server
    # Required-Start:       $remote_fs $syslog
    # Required-Stop:        $remote_fs $syslog
    # Should-Start:         $network
    # Should-Stop:          $network
    # Default-Start:        2 3 4 5
    # Default-Stop:         0 1 6
    # Short-Description:    Enterprise Resource Management software
    # Description:          Open ERP is a complete ERP and CRM software.
    ### END INIT INFO

    PATH=/bin:/sbin:/usr/bin
    DAEMON=/home/odoo/odoo/odoo.py
    NAME=odoo
    DESC=odoo

    # Specify the user name (Default: openerp).
    USER=odoo

    # Specify an alternate config file (Default: /etc/openerp-server.conf).
    CONFIGFILE="/home/odoo/odoo.conf"

    # pidfile
    PIDFILE=/var/run/$NAME.pid

    # Additional options that are passed to the Daemon.
    DAEMON_OPTS="-c $CONFIGFILE"

    [ -x $DAEMON ] || exit 0
    [ -f $CONFIGFILE ] || exit 0

    checkpid() {
        [ -f $PIDFILE ] || return 1
        pid=`cat $PIDFILE`
        [ -d /proc/$pid ] && return 0
        pid=`cat $PIDFILE`
        [ -d /proc/$pid ] && return 0
        return 1
    }

    case "${1}" in
            start)
                    echo -n "Starting ${DESC}: "

                    start-stop-daemon --start --quiet --pidfile ${PIDFILE} \
                            --chuid ${USER} --background --make-pidfile \
                            --exec ${DAEMON} -- ${DAEMON_OPTS}

                    echo "${NAME}."
                    ;;

            stop)
                    echo -n "Stopping ${DESC}: "

                    start-stop-daemon --stop --quiet --pidfile ${PIDFILE} \
                            --oknodo

                    echo "${NAME}."
                    ;;

            restart|force-reload)
                    echo -n "Restarting ${DESC}: "

                    start-stop-daemon --stop --quiet --pidfile ${PIDFILE} \
                            --oknodo

                    sleep 1

                    start-stop-daemon --start --quiet --pidfile ${PIDFILE} \
                            --chuid ${USER} --background --make-pidfile \
                            --exec ${DAEMON} -- ${DAEMON_OPTS}

                    echo "${NAME}."

                    echo "${NAME}."
                    ;;

            *)
                    N=/etc/init.d/${NAME}
                    echo "Usage: ${NAME} {start|stop|restart|force-reload}" >&2
                exit 1
                ;;
    esac

    exit 0

##### 4) donner les bons droits au fichier

    # chmod 755 /etc/init.d/odoo

##### 5) tester le script
    
    # /etc/init.d/odoo start

tester à nouveau sur localhost:8069

##### 6) faire en sorte que le script s'exécute au démarrage

    # update-rc.d odoo defaults


## Pour aller plus loin: proxy nginx

##### 1) installer nginx

    # apt-get install nginx

vous pouvez tester l'installation réussie sur http://localhost

##### 2) configurer nginx pour odoo : editer le fichier de conf

    # vim /etc/nginx/sites-enabled/default

supprimer le contenu et le remplacer par

    upstream odoo {
        server 127.0.0.1:8069 weight=1 fail_timeout=300s;
    }

    server {
            # server port and name
            listen        80;
            server_name   localhost;


            location / {
                    proxy_pass    http://odoo;
                    # force timeouts if the backend dies
                    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;

                    # set headers
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;

            }
    }

##### 3) tester la config et relancer nginx 

    # nginx -t
    # nginx -s reload

tester http://localhost

devrait conduire à odoo (ne pas oublier de vider le cache de son navigateur au cas ou ca ne marche pas tout de suite)

## Sécurité

> odoo plus accessible sur le port et changer le master password

a) editer fichier de conf de odoo

    # vim /home/odoo/odoo.conf

changer 

    admin_passwd = admin 
    xmlrpc_interface =

pour 

    admin_passwd = secret_password
    xmlrpc_interface = 127.0.0.1

b) redémarrer odoo

    # /etc/init.d/odoo restart

