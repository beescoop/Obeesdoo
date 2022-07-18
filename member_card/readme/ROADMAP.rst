**Customer Barcodes**

- odoo/base adds `barcode` field on `res.partner`.
- member_card also adds `barcode` but defines it as computed and stored.

On `member_card` install, odoo will compute the values for barcode field and **erase pre-existing values**.
It will also make it impossible to load data on that field.

**Member Card Template**

Integrate template developped for Polln here : `[ADD] member_card: add member card report
#289 <https://github.com/beescoop/Obeesdoo/pull/289>`_
