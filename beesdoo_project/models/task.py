# -*- coding: utf-8 -*-
'''
 Created on 5 déc. 2015

 @author: Thibault François
'''

from openerp import models, fields, api

class Task(models.Model):
    
    _inherit = 'project.task'
    
    author_id = fields.Many2one('res.users', string="Author")
    reviewer_id = fields.Many2one('res.users', string="Reviewer")
    tester_id = fields.Many2one('res.users', string="Tester")
    link_task_ids = fields.Many2many('project.task', 
                                     relation="link_task_relation_table", 
                                     column1='user1_id', 
                                     column2='user2_id', string="Linked Tasks")
    