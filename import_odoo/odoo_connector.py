'''
Created on 25 nov. 2014

@author: openerp
'''
from openerp import models, fields, api
import openerplib
from openerp.exceptions import Warning




class odoo_connection_data(models.Model):
    
    _name = 'import.odoo.connection'
    
    name = fields.Char("Name", required=True)
    host = fields.Char("Host", required=True)
    port = fields.Integer("Port", required=True, default=8069)
    database = fields.Char("Database", required=True)
    user = fields.Char("Login", required=True, default="admin")
    password = fields.Char("Password", required=True)
    protocol = fields.Selection([('xmlrpc', 'Xmlrpc'), ('jsonrpc', 'Jsonrpc'),('xmlrpcs', 'Xmlrpcs'), ('jsonrpcs', 'Jsonrpcs')], string="Protocol", default="xmlrpc")
    active = fields.Boolean("Active", default=True)
    
    @api.multi
    def test_connection(self):
        connection = self._get_connection()
        connection.check_login(force=True)
        raise Warning("Connection Successful")
    
    def _get_connection(self):
        return openerplib.get_connection(hostname=self.host, 
                                         port=self.port, 
                                         database=self.database, 
                                         login=self.user, 
                                         password=self.password, 
                                         protocol=self.protocol)
