# Copyright 2020 Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.cooperator_worker.tests import test_base


class TestWorkers(test_base.TestWorkerBase):
    def test_is_worker_still_set_for_worker_share(self):
        self.cooperator_x.worker_store = True
        self.assertEqual(self.cooperator_x.is_worker, True)

    def test_is_worker_forced_set_for_non_worker_share(self):
        self.cooperator_y.worker_store = True
        self.assertEqual(self.cooperator_y.is_worker, True)
