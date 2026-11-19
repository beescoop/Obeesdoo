# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade


def convert_product_barcode_generator_barcode_rule(env):
    barcode_rule = env.ref(
        "product_barcode_generator.product_barcode_generator_rule",
        raise_if_not_found=False,
    )
    if not barcode_rule:
        # barcode rule not found, nothing to do.
        return
    barcode_rule.write(
        {
            # ensure pattern is of form "{prefix}......." (12 characters, to
            # comply to ean-13 encoding).
            "pattern": barcode_rule.pattern + "." * (12 - len(barcode_rule.pattern)),
            "generate_type": "sequence",
            "generate_model": "product.product",
        }
    )
    # clear obsolete ir.model.data to ensure that the barcode rule does not
    # get deleted when the module is updated.
    env["ir.model.data"].search(
        [
            ("module", "=", "product_barcode_generator"),
            ("name", "=", "product_barcode_generator_rule"),
        ]
    ).unlink()


def convert_pos_price_to_weight_barcode_rule(env):
    barcode_rule = env.ref(
        "pos_price_to_weight.rule_price_to_weight", raise_if_not_found=False
    )
    if not barcode_rule:
        # barcode rule not found, nothing to do.
        return
    barcode_rule_vals = {
        "generate_type": "sequence",
        "generate_model": "product.product",
    }
    sequence = env.ref(
        "product_barcode_generator.seq_ean_product_internal_ref",
        raise_if_not_found=False,
    )
    if sequence:
        # rename the sequence to use the same name and code as the
        # auto-generated one instead of "Internal reference" and
        # "product.internal.code".
        sequence.write(
            {
                "name": "Sequence - Price Barcodes (Computed Weight)",
                "code": False,
            }
        )
        barcode_rule_vals["sequence_id"] = sequence.id
        # clear obsolete ir.model.data and ensure that the sequence does not
        # get deleted when the module is updated.
        env["ir.model.data"].search(
            [
                ("module", "=", "product_barcode_generator"),
                ("name", "=", "seq_ean_product_internal_ref"),
            ]
        ).unlink()
    barcode_rule.write(barcode_rule_vals)


@openupgrade.migrate()
def migrate(env, version):
    convert_product_barcode_generator_barcode_rule(env)
    convert_pos_price_to_weight_barcode_rule(env)
