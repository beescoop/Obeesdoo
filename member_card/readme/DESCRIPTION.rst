Create a member card and link it to a partner.

- Adds a member_card_template view and print option on partner
- Adds a "Member card" tab on the partner with a button to create a new member card
- The partner's card and barcode history is visible in the member card tab
- Creating a card generates a barcode, witch is then displayed on the member card
- The "Force Barcode" option allows to set a specific barcode instead
- A partner's barcode is computed from the last active member card
- Adds a field ``member_card_logo`` on the company allowing to upload an image
- The card template displays the ``member_card_logo`` image
- A boolean "Print Member card?" allows to flag partners for whom you need to print new cards.
- The wizards "Request member card printing" and "Set member card as printed" allow to mass check and uncheck the "Print Member Card?" flag.
- If the point of sale is installed, the generated barcode matches customer pattern rule.

The wizards "Request member card printing" and "Set member card as printed" allow to

Careful : this module overrides the barcodes already defined on the partners.

If point of sale is installed, the generated barcode matches customer pattern rule.
