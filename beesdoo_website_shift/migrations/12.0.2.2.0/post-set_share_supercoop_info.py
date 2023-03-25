# Copyright 2023 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # before this version, the module behaved as if then new
    # share_supercoop_info field was true. the default value of the field is
    # false, but the behavior must not change for databases that were already
    # using this module.
    cr.execute("update res_partner set share_supercoop_info = true where super")
