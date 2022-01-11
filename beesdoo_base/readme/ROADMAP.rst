**Customer Barcodes**

- odoo/base adds `barcode` field on `res.partner`.
- beesdoo_base also adds `barcode` but defines it as computed and stored.

On `beesdoo_base` install, odoo will compute the values for barcode field and **erase pre-existing values**.
It will also make it impossible to load data on that field.
