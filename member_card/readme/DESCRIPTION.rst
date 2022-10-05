Create a member card and link it to a partner.

- each member card has a barcode
- create new cards in the "member card" tab of the partner form
- use "Force Barcode" field to set a user defined barcode
- the partner's card and barcode history is visible in the member card tab
- the barcode of a partner is computed from the last active member card
- a boolean "Print Member card?" allows to filter on partners for which you need to print new cards.
- contains a generic template for the member card
- the card template uses field `member_card_logo` rather than the company logo

The wizards "Request member card printing" and "Set member card as printed" allow to

Careful : this module overrides the barcodes already defined on the partners.

If point of sale is installed, the generated barcode matches customer pattern rule.
