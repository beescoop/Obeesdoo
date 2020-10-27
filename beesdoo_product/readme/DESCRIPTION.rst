Modification of product module for the needs of beescoop
- SOOO5 - Adds the label bio/ethique/provenance
- Add a 'Suggested Price' field on products, and a 'Product Margin' field on Partners (Vendors) and Product Categories. The first margin is used if set, otherwise the second margin (which has a default value) is used.
- The reference price on which this margin is applied (supplier price or sale price) can be selected in the general settings.
- Also, sale and supplier taxes that are of type 'percentage' and that are marked as 'included in price' are taken into account when computing the suggested price.

Please note that this model makes assumptions when computing the suggested price:
- It supposes that each product has only one supplier and that products coming from multiple suppliers occure as duplicated products with one supplier each.
