12.0.1.2.0 (2022-11-08)
~~~~~~~~~~~~~~~~~~~~~~~

**Features**

- Bigger product name, even bigger price, bigger price info, bigger
  labels. But now labels stick on one line only (as there will be no more
  than 4 or maybe a bit more with some devs). Also adds more space between
  labels (horizontally only). (`#452-1 <https://github.com/beescoop/Obeesdoo/issues/452-1>`_)
- Change what's shown on the second line of the pricetag. It shows the product
  brand, and, if not set, show the main seller name. The module depend on
  the ``product_brand`` module (from `product-attribute
  <https://github.com/OCA/product-attribute>`_). (`#452 <https://github.com/beescoop/Obeesdoo/issues/452>`_)


**Bugfixes**

- Trigger printing of new pricetag when the field *Price* is modified. (`#452 <https://github.com/beescoop/Obeesdoo/issues/452>`_)


12.0.1.1.4 (2022-09-23)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Refactor default pricetag to fit right size and prevent overflow of
  content. (`#448 <https://github.com/beescoop/Obeesdoo/issues/448>`_)
