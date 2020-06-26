![Licence](https://img.shields.io/badge/licence-AGPL--3-blue.svg)
[![Build Status](https://travis-ci.org/beescoop/Obeesdoo.svg?branch=12.0)](https://travis-ci.org/beescoop/Obeesdoo.svg?branch=12.0)

# Obeesdoo
Specific module for the Beescoop


<!-- prettier-ignore-start -->
[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[beesdoo_account](beesdoo_account/) | 12.0.1.0.0 | Makes date_invoice field required in account.invoice_form and account.invoice_supplier_form
[beesdoo_base](beesdoo_base/) | 12.0.1.0.0 | Module that customize the base module and contains some python tools
[beesdoo_crelan_csv](beesdoo_crelan_csv/) | 12.0.1.0.0 | Import Crelan CSV Wizard
[beesdoo_easy_my_coop](beesdoo_easy_my_coop/) | 12.0.1.0.0 | Link between beesdoo customization and easy_my_coop
[beesdoo_inventory](beesdoo_inventory/) | 12.0.1.0.0 | Adds a responsible, a max shipping date and a button to copy quantity to stock pickings.
[beesdoo_pos](beesdoo_pos/) | 12.0.1.0.0 | This module adds the eaters of the customer to the POS ActionpadWidget and PaymentScreenWidget.
[beesdoo_pos_reporting](beesdoo_pos_reporting/) | 12.0.1.0.0 | Enhance POS with features allowing statistics and reporting.
[beesdoo_product](beesdoo_product/) | 12.0.1.0.0 | Modification of product module for the needs of beescoop - SOOO5 - Ajout de label bio/ethique/provenance
[beesdoo_product_usability](beesdoo_product_usability/) | 12.0.1.0.0 | Adapt the product views.
[beesdoo_purchase](beesdoo_purchase/) | 12.0.1.1.0 | - Adds a 'Responsible' field to purchase orders, - A filter w.r.t. the mail sellers is placed on the products field of a purchase order.
[beesdoo_shift](beesdoo_shift/) | 12.0.1.0.0 | Generate and manage shifts for cooperators.
[beesdoo_shift_attendance](beesdoo_shift_attendance/) | 12.0.1.0.1 | Volonteer Timetable Management Attendance Sheet for BEES coop
[beesdoo_stock](beesdoo_stock/) | 12.0.1.0.0 | Enable action on multiple products of a stock receipt
[beesdoo_stock_coverage](beesdoo_stock_coverage/) | 12.0.0.0.1 | Compute estimated stock coverage based on product sales over a date range.
[beesdoo_website_eater](beesdoo_website_eater/) | 12.0.1.0.0 | Show the eaters of a cooperator in the website portal.
[beesdoo_website_posorder_amount](beesdoo_website_posorder_amount/) | 12.0.1.0.0 | Show the total amount of pos order in the website portal.
[beesdoo_website_shift](beesdoo_website_shift/) | 12.0.1.0.0 | Show available shifts for regular and irregular workers on the website and let workers manage their shifts with an easy web interface.
[beesdoo_website_theme](beesdoo_website_theme/) | 12.0.0.0.1 | Apply BEES coop design rules.
[beesdoo_worker_status](beesdoo_worker_status/) | 12.0.1.0.0 | Worker status management specific to beescoop.
[macavrac_base](macavrac_base/) | 12.0.1.0.0 | Module with basic customizations for the Macavrac cooperative.
[purchase_order_generator](purchase_order_generator/) | 12.0.1.0.0 | Generate purchase order from a product selection
[website_portal_restrict_modification](website_portal_restrict_modification/) | 12.0.1.0.0 | Portal extension preventing modification of sensible data by the users

[//]: # (end addons)
<!-- prettier-ignore-end -->

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
$ git clone https://github.com/OCA/partner-contact.git partner-contact -b 12.0 --depth 1
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
    $ODOO_HOME/partner-contact,
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
