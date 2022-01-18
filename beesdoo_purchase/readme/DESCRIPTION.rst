Extends Purchase module:

- Adds a 'Responsible' field to purchase orders:
  This is a user who will follow up the order. This users replaces
  the creator in the order's mail messages followers list, and in the
  create_uid ORM field. His user's contact info is printed on
  purchases orders as 'Referent'.
- A filter w.r.t. the mail sellers is placed on the products field of a
  purchase order.
- Allows inverting the Purchase Order (PO) Reference on the invoice lines.
- Allows adapting a product's purchase and/or selling price from a PO.
