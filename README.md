
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/beescoop/obeesdoo/actions/workflows/pre-commit.yml/badge.svg?branch=12.0)](https://github.com/beescoop/obeesdoo/actions/workflows/pre-commit.yml?query=branch%3A12.0)
[![Build Status](https://github.com/beescoop/obeesdoo/actions/workflows/test.yml/badge.svg?branch=12.0)](https://github.com/beescoop/obeesdoo/actions/workflows/test.yml?query=branch%3A12.0)
[![codecov](https://codecov.io/gh/beescoop/obeesdoo/branch/12.0/graph/badge.svg)](https://codecov.io/gh/beescoop/obeesdoo)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Obeesdoo

Specific modules for the BEES coop

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[beesdoo_account](beesdoo_account/) | 12.0.2.0.1 |  | Emptied.
[beesdoo_base](beesdoo_base/) | 12.0.2.0.1 |  | Emptied
[beesdoo_crelan_csv](beesdoo_crelan_csv/) | 12.0.2.0.0 |  | Emptied
[beesdoo_easy_my_coop](beesdoo_easy_my_coop/) | 12.0.1.2.2 |  | Emptied.
[beesdoo_inventory](beesdoo_inventory/) | 12.0.3.1.0 |  | Emptied. leftover: Restrict selectable products to those sold as main supplier by the picking partner.
[beesdoo_pos](beesdoo_pos/) | 12.0.3.0.0 |  | Emptied.
[beesdoo_pos_coop_status](beesdoo_pos_coop_status/) | 12.0.2.1.1 |  | Emptied.
[beesdoo_pos_email_ticket](beesdoo_pos_email_ticket/) | 12.0.1.1.0 |  | This module adds the eaters of the customer to the POS ActionpadWidget and PaymentScreenWidget.
[beesdoo_pos_reporting](beesdoo_pos_reporting/) | 12.0.1.0.0 |  | Emptied.
[beesdoo_print_label](beesdoo_print_label/) | 12.0.2.0.0 |  | Product labels
[beesdoo_product](beesdoo_product/) | 12.0.3.0.0 |  | Emptied.
[beesdoo_product_info_screen](beesdoo_product_info_screen/) | 12.0.0.0.1 |  | Adds a read-only screen to display product information
[beesdoo_product_label](beesdoo_product_label/) | 12.0.3.0.1 |  | Adds the label bio/ethique/provenance.
[beesdoo_product_usability](beesdoo_product_usability/) | 12.0.2.0.1 |  | Emptied. Leftover: simplification of Product View.
[beesdoo_purchase](beesdoo_purchase/) | 12.0.1.4.0 |  | Enhancements related to Purchase module : field, filter, PO reference, product's purchase and/or selling price
[beesdoo_shift](beesdoo_shift/) | 12.0.4.0.0 |  | Emptied (replaced by shift)
[beesdoo_shift_attendance](beesdoo_shift_attendance/) | 12.0.1.2.0 |  | Emptied (replaced by shift_attendance)
[beesdoo_shift_swap](beesdoo_shift_swap/) | 12.0.2.1.1 |  | Module to allow cooperator to swap his/her shift when he/she can't attend it, to do solidarity shifts, and to request solidarity if needed.
[beesdoo_shift_welcome_screen](beesdoo_shift_welcome_screen/) | 12.0.1.0.2 |  | Volunteer Timetable Management
[beesdoo_stock](beesdoo_stock/) | 12.0.2.0.0 |  | Emptied
[beesdoo_stock_coverage](beesdoo_stock_coverage/) | 12.0.2.0.0 |  | Emptied
[beesdoo_website_eater](beesdoo_website_eater/) | 12.0.2.0.1 |  | Emptied.
[beesdoo_website_posorder_amount](beesdoo_website_posorder_amount/) | 12.0.1.0.0 |  | Show the total amount of pos order in the website portal.
[beesdoo_website_shift](beesdoo_website_shift/) | 12.0.2.1.1 |  | Show available shifts for regular and irregular workers on the website and let workers manage their shifts with an easy web interface.
[beesdoo_website_shift_swap](beesdoo_website_shift_swap/) | 12.0.2.1.0 |  | Add shift exchanges and solidarity shifts offers and requests.
[beesdoo_website_theme](beesdoo_website_theme/) | 12.0.0.0.1 |  | Apply BEES coop design rules.
[beesdoo_worker_status](beesdoo_worker_status/) | 12.0.1.1.0 |  | Emptied (replaced by shift_worker_status)
[beesdoo_worker_status_shift_swap](beesdoo_worker_status_shift_swap/) | 12.0.2.0.1 |  | Worker status management specific to shift exchanges.
[cooperator_eater](cooperator_eater/) | 12.0.1.0.2 |  | Eater configuration based on Share product
[cooperator_info_session](cooperator_info_session/) | 12.0.1.0.3 |  | Info session for getting share
[cooperator_worker](cooperator_worker/) | 12.0.2.0.1 |  | Working and shopping configuration based on Share product
[cooperator_worker_force](cooperator_worker_force/) | 12.0.2.0.1 |  | Allows to set a cooperator as a worker before the share is released.
[eater](eater/) | 12.0.1.0.0 |  | Add eaters to the workers of your structure.
[eater_member_card](eater_member_card/) | 12.0.1.1.0 |  | Compute barcode based on eaters
[eater_parent_barcode](eater_parent_barcode/) | 12.0.1.0.0 |  | Compute barcode based on eaters
[macavrac_base](macavrac_base/) | 12.0.1.0.1 |  | Module with basic customizations for the Macavrac cooperative.
[member_card](member_card/) | 12.0.1.0.1 |  | Create a member card and link it to a partner.
[polln_shift](polln_shift/) | 12.0.2.0.1 |  | Module with basic customizations for the Polln cooperative.
[portal_eater](portal_eater/) | 12.0.2.0.1 |  | Show the eaters of a cooperator in the website portal.
[pos_auto_invoice_company](pos_auto_invoice_company/) | 12.0.3.0.0 |  | Applies to_invoice to company partners.
[pos_eater](pos_eater/) | 12.0.2.0.0 |  | This module adds the eaters of the customer to the POS ActionpadWidget.
[pos_shift_partner_can_shop](pos_shift_partner_can_shop/) | 12.0.2.0.2 |  | Display in the POS whether the partner can shop or not.
[product_barcode_generator](product_barcode_generator/) | 12.0.1.0.0 | [![victor-champonnois](https://github.com/victor-champonnois.png?size=30px)](https://github.com/victor-champonnois) | Product Barcode Generator
[product_expiration](product_expiration/) | 12.0.2.0.0 |  | Add Number of Days Before Product Expiration.
[product_hazard](product_hazard/) | 12.0.1.0.0 |  | Add hazard and FDS labels to products
[product_ingredients](product_ingredients/) | 12.0.1.0.0 |  | Adds an 'Ingredients' field to products
[product_label_print_request](product_label_print_request/) | 12.0.1.0.0 | [![victor-champonnois](https://github.com/victor-champonnois.png?size=30px)](https://github.com/victor-champonnois) | Facilitation for label printing.
[product_main_supplier](product_main_supplier/) | 12.0.2.0.0 |  | Add a main supplier
[product_sale_limit_date](product_sale_limit_date/) | 12.0.2.0.0 |  | Add Number of Days Before Sale Limit Date.
[product_scale_label](product_scale_label/) | 12.0.2.0.0 |  | Add scale labels, sale units, and categories.
[purchase_order_generator](purchase_order_generator/) | 12.0.2.1.0 |  | Generate purchase order from a product selection
[sale_adapt_price_wizard](sale_adapt_price_wizard/) | 12.0.1.0.1 |  | Add "Edit Price" submenu on Purchase and Sale modules.
[sale_product_deposit](sale_product_deposit/) | 12.0.1.0.1 |  | Calculates total price with VAT and deposit price.
[sale_suggested_price](sale_suggested_price/) | 12.0.1.0.0 |  | Add a suggested price to products, dependent on a product margin in partners and product categories.
[shift](shift/) | 12.0.5.0.0 |  | Generate and manage shifts for cooperators.
[shift_attendance](shift_attendance/) | 12.0.2.0.0 |  | Volunteer Timetable Management
[shift_worker_status](shift_worker_status/) | 12.0.2.0.0 |  | Worker status management.
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
