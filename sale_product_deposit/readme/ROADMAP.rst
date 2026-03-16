Using taxes as deposits is deprecated and should be removed in the future.
Instead, a deposit product should be used (using ``pos_container_deposit``).
Using taxes is currently still supported to allow for an easier manual transition to deposit products.
Eventually, the tax group defined in this module will be removed and the remaining taxes should be converted to products by a migration script.

This module uses the (gross) ``weight`` field of the product to compute the price per base unit.
This is not very clean, as this field is supposed to contain the gross weight (not the net weight, which should be used to compute the price), and it is only a weight, while this module uses its value also for other UoM categories.

This module is not multi-company compatible: taxes are defined per company, but this module defines stored computed fields (that depends on taxes) on products, which can be shared by multiple companies.
Currently, all taxes defined on the products are used to compute these fields, regardless of the company they are linked to.
