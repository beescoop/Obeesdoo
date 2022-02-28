Modification of product module for the needs of beescoop

- Adds the label bio/ethique/provenance.
- Adds hazard and FDS labels.
- Adds a main seller.
- Calculates total price with VAT and deposit price.
- Contains some facilitation for label printing.
- Adds a 'Comments' field for use on labels.
- Adds deadline for sale and consumption.
- Adds an 'Ingredients' field.
- Adds scale labels, sale units, and categories.
- Generates barcodes.
- Adds a 'Suggested Price' field on products, and a 'Product Margin' field on Partners (Vendors) and Product Categories.
  The first margin is used if set, otherwise the second margin (which has a default value) is used.
- The reference price on which this margin is applied (supplier price or sale price)
  can be selected in the general settings.
- Also, sale and supplier taxes that are of type 'percentage' and that are marked as 'included in price'
  are taken into account when computing the suggested price.
- Round suggested price to 5 cents
- Adds "Edit Price" submenu on Point Of Sale, Purchase and Sale modules.
  The user lands on an editable List View with the following columns :

  - Name (`name`)
  - Main Seller (`main_seller_id`)
  - Purchase Price (`purchase_price`)
  - Purchase Unit of Measure (`uom_po_id`)
  - Suggested Price (`suggested_price`)
  - Sales Price (`list_price`)
  - Unit of Measure (`uom_id`)

  The only editable field is Purchase Price.
  Through "Action > Adapt Sales Price", the user can, on the selected products,
  adapt the Sales Price according to the Suggested Price.

Please note that this model makes assumptions when computing the suggested price:

- It supposes that each product has only one supplier and that products coming from multiple suppliers
  occur as duplicated products with one supplier each.
