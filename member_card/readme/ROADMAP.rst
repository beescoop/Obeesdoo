- factor out wizards "request member card printing" and "set member card as printed"

  - it was used to request a batch of card to print but has no link to the actual template
- use ``barcodes_generator_abstract`` from the OCA to generate barcodes

**Customer Barcodes**

- odoo/base adds ``barcode`` field on ``res.partner``.
- member_card also adds ``barcode`` but defines it as computed and stored.

On ``member_card`` install, odoo will compute the values for barcode field and **erase pre-existing values**.
It will also make it impossible to load data on that field.
