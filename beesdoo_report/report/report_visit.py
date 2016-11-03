# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api

#----------------
class ReportVisit(models.Model):
    _name = "beesdoo.report.visits"
    _description = "Labo Market Visit"
    _auto = False
    _order = 'week desc'

    week = fields.Date("Week")
    type = fields.Char()
    visitors = fields.Integer("Visitors")
    visits = fields.Integer("Visits")
    #gross_sale = fields.Float("Gross Sales")

    def init(self, cr):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW beesdoo_report_visits as (
        select 
            row_number() over() as id, 
            week,
            type,
            visits
        from(
            select
              date_trunc('WEEK',  date_order )::date as week,
              count (distinct partner_id) + sum (case when partner_id is null then 1 else 0 end ) - 1 as visits,
              'visites_uniques' as type
            from
              pos_order
            group by
              date_trunc('WEEK', date_order)
             union  
            select
              date_trunc('WEEK',  date_order )::date as week,
              count (distinct id) as visits,
              'visites' as type
            from
              pos_order
            group by
              date_trunc('WEEK', date_order)
              ) t
        
        order by
          week, type desc
     
        )""")