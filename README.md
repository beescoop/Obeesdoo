
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/beescoop/obeesdoo/actions/workflows/pre-commit.yml/badge.svg?branch=12.0)](https://github.com/beescoop/obeesdoo/actions/workflows/pre-commit.yml?query=branch%3A12.0)
[![Build Status](https://github.com/beescoop/obeesdoo/actions/workflows/test.yml/badge.svg?branch=12.0)](https://github.com/beescoop/obeesdoo/actions/workflows/test.yml?query=branch%3A12.0)
[![codecov](https://codecov.io/gh/beescoop/obeesdoo/branch/12.0/graph/badge.svg)](https://codecov.io/gh/beescoop/obeesdoo)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Obeesdoo

Specific module for the Beescoop
The (french) documentation can be found here.
Contact Coop IT Easy or Coopdevs to contibute to the documentation.


<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[beesdoo_account](beesdoo_account/) | 12.0.2.0.0 |  | - Makes date_invoice field required in account.invoice_form and account.invoice_supplier_form - Allow validating an invoice with a negative total amount
[beesdoo_base](beesdoo_base/) | 12.0.2.0.0 |  | Module that customize the base module and contains some python tools
[beesdoo_crelan_csv](beesdoo_crelan_csv/) | 12.0.1.0.0 |  | Import Crelan CSV Wizard
[beesdoo_easy_my_coop](beesdoo_easy_my_coop/) | 12.0.1.0.2 |  | Link between beesdoo customization and easy_my_coop
[beesdoo_inventory](beesdoo_inventory/) | 12.0.3.0.1 |  | Restrict selectable products to those sold as main supplier by the picking partner.
[beesdoo_pos](beesdoo_pos/) | 12.0.2.0.0 |  | This module adds the eaters of the customer to the POS ActionpadWidget and PaymentScreenWidget.
[beesdoo_pos_coop_status](beesdoo_pos_coop_status/) | 12.0.1.0.0 |  | POS Support for cooperator status.
[beesdoo_pos_email_ticket](beesdoo_pos_email_ticket/) | 12.0.1.1.0 |  | This module adds the eaters of the customer to the POS ActionpadWidget and PaymentScreenWidget.
[beesdoo_pos_reporting](beesdoo_pos_reporting/) | 12.0.1.0.0 |  | Enhance POS with features allowing statistics and reporting.
[beesdoo_print_label](beesdoo_print_label/) | 12.0.1.1.2 |  | Product labels
[beesdoo_product](beesdoo_product/) | 12.0.1.4.1 |  | Modification of product module for the needs of beescoop
[beesdoo_product_info_screen](beesdoo_product_info_screen/) | 12.0.0.0.1 |  | Adds a read-only screen to display product information
[beesdoo_product_usability](beesdoo_product_usability/) | 12.0.1.0.0 |  | Adapt the product views.
[beesdoo_purchase](beesdoo_purchase/) | 12.0.1.4.0 |  | Enhancements related to Purchase module : field, filter, PO reference, product's purchase and/or selling price
[beesdoo_shift](beesdoo_shift/) | 12.0.3.1.0 |  | Generate and manage shifts for cooperators.
[beesdoo_shift_attendance](beesdoo_shift_attendance/) | 12.0.1.1.2 |  | Volonteer Timetable Management Attendance Sheet for BEES coop
[beesdoo_shift_swap](beesdoo_shift_swap/) | 12.0.2.1.0 |  | Module to allow cooperator to swap his/her shift when he/she can't attend it, to do solidarity shifts, and to request solidarity if needed.
[beesdoo_shift_welcome_screen](beesdoo_shift_welcome_screen/) | 12.0.1.0.1 |  | Volunteer Timetable Management
[beesdoo_stock](beesdoo_stock/) | 12.0.1.0.0 |  | Enable action on multiple products of a stock receipt
[beesdoo_stock_coverage](beesdoo_stock_coverage/) | 12.0.0.0.1 |  | Compute estimated stock coverage based on product sales over a date range.
[beesdoo_website_eater](beesdoo_website_eater/) | 12.0.1.0.0 |  | Show the eaters of a cooperator in the website portal.
[beesdoo_website_posorder_amount](beesdoo_website_posorder_amount/) | 12.0.1.0.0 |  | Show the total amount of pos order in the website portal.
[beesdoo_website_shift](beesdoo_website_shift/) | 12.0.2.1.0 |  | Show available shifts for regular and irregular workers on the website and let workers manage their shifts with an easy web interface.
[beesdoo_website_shift_swap](beesdoo_website_shift_swap/) | 12.0.2.1.0 |  | Add shift exchanges and solidarity shifts offers and requests.
[beesdoo_website_theme](beesdoo_website_theme/) | 12.0.0.0.1 |  | Apply BEES coop design rules.
[beesdoo_worker_status](beesdoo_worker_status/) | 12.0.1.1.0 |  | Worker status management specific to beescoop.
[beesdoo_worker_status_shift_swap](beesdoo_worker_status_shift_swap/) | 12.0.2.0.0 |  | Worker status management specific to shift exchanges.
[eater](eater/) | 12.0.1.0.0 |  | Add eaters to the workers of your structure.
[eater_member_card](eater_member_card/) | 12.0.1.0.0 |  | Compute barcode based on eaters
[macavrac_base](macavrac_base/) | 12.0.1.0.0 |  | Module with basic customizations for the Macavrac cooperative.
[member_card](member_card/) | 12.0.1.0.1 |  | Create a member card and link it to a partner.
[polln_shift](polln_shift/) | 12.0.1.0.0 |  | Module with basic customizations for the Polln cooperative.
[purchase_order_generator](purchase_order_generator/) | 12.0.2.1.0 |  | Generate purchase order from a product selection
[stock_move_view_line_order](stock_move_view_line_order/) | 12.0.2.1.0 |  | Reverse the order of stock move lines to 'newest to oldest'.
[website_portal_restrict_modification](website_portal_restrict_modification/) | 12.0.1.0.0 |  | Portal extension preventing modification of sensible data by the users

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

## Install odoo (deprecrated)

- cf. [install-odoo-linux-server.md](install-odoo-linux-server.md) (review)
- cf. [install-odoo-linux.md](install-odoo.md) (review)
- cf. [install-odoo-mac.md](install-odoo-mac.md)
- cf. [install-odoo-docker.md](install-odoo-docker.md)

## Setup obeesdoo (deprecrated)

##### 1) clone repos

```
$ cd projects
$ git clone https://github.com/beescoop/Obeesdoo.git obeesdoo -b 12.0 --depth 1
$ git clone https://github.com/coopiteasy/vertical-cooperative.git vertical-cooperative -b 12.0 --depth 1
$ git clone https://github.com/coopiteasy/addons.git addons -b 12.0 --depth 1
$ git clone https://github.com/OCA/partner-contact.git partner-contact -b 12.0 --depth 1
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


## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Coop IT Easy SC
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
