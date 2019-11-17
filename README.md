# Obeesdoo
Specific module for the Beescoop


## Migration to 12.0

**Do not migrate the following modules**:
- `admin_technical_features`
- `base_technical_features`
- `beesdoo_coda`
- `beesdoo_crelan_csv` vérifier s'il n'existe pas dans l'oca.
- `mass_editing`
- `pos_price_to_weigth` Attention il y a eu des modification de Houssine.
- `web_environment_ribbon`

## Install odoo

- cf. [install-odoo-linux-server.md](install-odoo-linux-server.md) (review)
- cf. [install-odoo-linux.md](install-odoo.md) (review)
- cf. [install-odoo-mac.md](install-odoo-mac.md)
- cf. [install-odoo-docker.md](install-odoo-docker.md)

## Setup obeesdoo

##### 1) clone repos

```
$ cd projects
$ git clone https://github.com/beescoop/Obeesdoo.git obeesdoo -b 12.0 --depth 1
$ git clone https://github.com/coopiteasy/vertical-cooperative.git vertical-cooperative -b 12.0 --depth 1
$ git clone https://github.com/coopiteasy/addons.git addons -b 12.0 --depth 1
# $ git clone https://github.com/coopiteasy/procurement-addons procurement-addons -b 12.0 --depth 1
$ git clone https://github.com/OCA/l10n-belgium -b 12.0 --depth 1
$ git clone https://github.com/OCA/mis-builder -b 12.0 --depth 1
$ git clone https://github.com/OCA/account-financial-tools -b 12.0 --depth 1
$ git clone https://github.com/OCA/account-financial-reporting -b 12.0 --depth 1
$ git clone https://github.com/OCA/web -b 12.0 --depth 1
$ git clone https://github.com/OCA/website -b 12.0 --depth 1
$ git clone https://github.com/OCA/server-tools -b 12.0 --depth 1
$ git clone https://github.com/OCA/reporting-engine -b 12.0 --depth 1
$ git clone https://github.com/OCA/bank-payment.git -b 12.0 --depth 1
$ git clone https://github.com/OCA/pos.git -b 12.0 --depth 1
```

todo: setup git submodules

##### 2) install wkhtmltopdf

Download and install [wkhtmltopdf version 0.12.5](https://github.com/wkhtmltopdf/wkhtmltopdf/releases/0.12.5)

##### 3) set up the database and import production data.


```
$ createuser -d odoo
$ createdb beescoop -o odoo
$ gunzip <dump-file>.sql.gz
$ psql beescoop < <dump-file>.sql
```

##### 4) deactivate cron jobs and mails 

```
$ psql -d beescoop -c "UPDATE ir_cron SET active='f' WHERE active='t';"
$ psql -d beescoop -c "update ir_mail_server set smtp_encryption='none', smtp_port=1025, smtp_host='localhost',smtp_user='', smtp_pass='';"
$ psql -d beescoop -c "UPDATE fetchmail_server SET active='f', password='', server='localhost';"
```

##### 5) create odoo.conf

```
$ export ODOO_HOME='~/projects'
$ vi $ODOO_HOME/odoo.conf
```

```
[options]
; This is the password that allows database operations:
; admin_passwd = admin
debug=True
dev=True
db_host=False
db_port=False
db_user=odoo
db_password=False
addons_path=addons,openerp/addons,
    $ODOO_HOME/obeesdoo,
    $ODOO_HOME/vertical-cooperative,
    $ODOO_HOME/addons,
#    $ODOO_HOME/procurement-addons,
    $ODOO_HOME/l10n-belgium,
    $ODOO_HOME/mis-builder,
    $ODOO_HOME/web,
    $ODOO_HOME/website,
    $ODOO_HOME/server-tools,
    $ODOO_HOME/account-financial-reporting,
    $ODOO_HOME/account-financial-tools,
    $ODOO_HOME/bank-payment,
    $ODOO_HOME/pos,
    $ODOO_HOME/reporting-engine
```

##### 6) update database structure

```
$ cd ~/projects/odoo
$ psql -d beescoop -c "truncate product_scale_log"
$ python odoo.py -c $ODOO_HOME/odoo.conf -u all -d beescoop --stop-after-init
```

### Troubleshoot

 Missing libraries

 ```
 pip install pycoda
 pip install xlsxwriter
 ```

 Can't update `product_scale_log` table (I did not write down the exact error)

 ```
 truncate table product_scale_log
 ```

## Migrate barcode

```sql
insert into member_card (active, barcode, partner_id, responsible_id, activation_date) select 't', barcode, id, 1, '2016-01-01' from res_partner where barcode is not null;
update res_partner set eater = 'worker_eater' where barcode is not null;
```

