"""
def test(slot):
     last_sequence = int(self.env["ir.config_parameter"].sudo().get_param("last_planning_seq"))
     next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)
     next_planning_date = fields.Datetime.from_string(self.env["ir.config_parameter"].sudo().get_param("next_planning_date",0))
     next_swap_limit = int(self.env["ir.config_parameter"].sudo().get_param("beesdoo_shift.day_limit_swap"))
     end_date = slot.date + timedelta(days=next_swap_limit)
     shift_recset = self.env["beesdoo.shift.shift"]
     while next_planning_date < end_date :
             shift_recset |= next_planning.task_template_ids._generate_task_day()
             next_planning_date = next_planning._get_next_planning_date(next_planning_date)
             last_sequence = next_planning.sequence
             next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)
             next_planning = next_planning.with_context(visualize_date=next_planning_date)
     return shift_recset
"""
