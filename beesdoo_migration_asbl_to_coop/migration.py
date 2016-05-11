# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning

from openerp.addons.import_base.import_framework import *
from openerp.addons.import_base.mapper import *


class odoo_connection_data(models.TransientModel):
    
    _name = 'beesdoo.import.asbl'
    
    @api.multi
    def migrate(self):
        imp = migration_framework(self, self.env.cr, self.env.uid, "Odoo", 'beesdoo.import.asbl', dict(self.env.context))
        imp.launch_import()
    

class migration_framework(import_framework):
    black_list_field = {
                    
    }
    
    tables =  ['product.category',
               'product.uom',
               'product.uom.categ',
               'pos.category',
               'res.partner',
               'product.template',
               'product.supplierinfo',
    ]
               
    table_domain = {
        'res.partner' : [('supplier', '=', True), '|', ('active', '=', True), ('active', '=', False)],
        'product.template' : ['|', ('active', '=', True), ('active', '=', False)]
    }

    
    def initialize(self):
        self.connection = self.obj.env['import.odoo.connection'].search([], limit=1)
        self.set_table_list(self.tables)
        print self.connection.name
        
    def _get_field(self, model):
        fields = ['id']
        
        for mapper_object in self.get_mapping()[model.model_name]['map'].values():
            if isinstance(mapper_object, basestring):
                fields.append(mapper_object)
            else:
                fields.extend(mapper_object.get_fields())
        print "read field", fields
        return fields
    
    def res_to_dict(self, fields, datas):
        datas = datas['datas']
        res = []
        for data in datas:
            data_dict = {}
            for i, field in enumerate(fields):
                data_dict[field] = data[i]
            res.append(data_dict)
        return res
        
    def get_data(self, table):
        con = self.connection._get_connection()
        obj = con.get_model(table)
        fields = self._get_field(obj)
        ids = obj.search(self.table_domain.get(table, []))
        datas = obj.export_data(ids, fields, context={'lang' : 'fr_BE'})
        return self.res_to_dict(fields, datas)

    def _generate_xml_id(self, name, table):
        """
            @param name: name of the object, has to be unique in for a given table
            @param table : table where the record we want generate come from
            @return: a unique xml id for record, the xml_id will be the same given the same table and same name
                     To be used to avoid duplication of data that don't have ids
        """
        return name
    
    taxes_mapping = {
        '5.5% Marchandise' : '6% Marchandises',
        '6% Marchandise' : '6% Marchandises',
        '21% Services incluse' : '21% Services',
    }
 

    def get_mapping(self):
        return {
            'product.category': { 
                'model' : 'product.category',
                'dependencies' : [],
                'map' : {
                    'name' : 'name',
                    'parent_id/id_parent' : 'parent_id/id',
                    'type' : 'type',
                    
                }
            },
            'product.uom.categ' : {
                'model' : 'product.uom.categ',
                'dependencies' : [],
                'map' : {
                    'name' : 'name',
                }
            },
            'product.uom': { 
                'model' : 'product.uom',
                'dependencies' : ['product.uom.categ'],
                'map' : {
                    'name' : 'name',
                    'category_id/id' : 'category_id/id',
                    'rounding' : 'rounding',
                    'uom_type' : 'uom_type',
                    'factor' : 'factor',
                    'factor_inv' : 'factor_inv',
                }
            },
            'pos.category': { 
                'model' : 'pos.category',
                'dependencies' : [],
                'map' : {
                    'id' : 'id',
                    'name' : 'name',
                    'parent_id/id_parent' : 'parent_id/id',
                }
            },
            'res.partner': { 
                'model' : 'res.partner',
                'dependencies' : [],
                'map' : {
                    'active' : 'active',
                    'barcode' : 'barcode',
                    'birthdate' : 'birthdate',
                    'city' : 'city',
                    'comment' : 'comment',
                    'company_type' : 'company_type',
                    'contact_address' : 'contact_address',
                    'country_id/id' : 'country_id/id',
                    'email' : 'email',
                    'employee' : 'employee',
                    'fax' : 'fax',
                    'first_name' : 'first_name',
                    'function' : 'function',
                    'is_company' : 'is_company',
                    'lang' : 'lang',
                    'last_name' : 'last_name',
                    'mobile' : 'mobile',
                    'name' : 'name',
                    'parent_id/id_parent' : 'parent_id/id',
                    'phone' : 'phone',
                    'ref' : 'ref',
                    'street' : 'street',
                    'street2' : 'street2',
                    'supplier' : 'supplier',
                    'website' : 'website',
                    'zip' : 'zip',  
                    'supplier' : 'supplier',
                    'customer' : 'customer',
                    'vat' : 'vat',
                }
            },
            'beesdoo.product.label' : {
                'model' : 'beesdoo.product.label',
                'dependencies' : [],
                'map' : {
                    'color_code' : 'color_code',
                    'name' : 'name',
                    'type' : 'type',
                }
            },
            'product.template': { 
                'model' : 'product.template',
                'dependencies' : ['pos.category', 'product.category', 'beesdoo.product.label'],
                'map' : {
                    'active' : 'active',
                               'available_in_pos' : 'available_in_pos',
                               'barcode' : 'barcode',
                               'categ_id/id' : 'categ_id/id',
                               'default_code' : 'default_code',
                               'description' : 'description',
                               'description_picking' : 'description_picking',
                               'description_purchase' : 'description_purchase',
                               'description_sale' : 'description_sale',
                               'eco_label/id' : 'eco_label/id',
                               'fair_label/id' : 'fair_label/id',
                               'invoice_policy' : 'invoice_policy',
                               'local_label/id' : 'local_label/id',
                               'name' : 'name',
                               'origin_label/id' : 'origin_label/id',
                               'pos_categ_id/id' : 'pos_categ_id/id',
                               'purchase_ok' : 'purchase_ok',
                               'sale_delay' : 'sale_delay',
                               'sale_ok' : 'sale_ok',
                               'standard_price' : 'standard_price',
                               'supplier_taxes_id' : map_val_default('supplier_taxes_id', self.taxes_mapping),  #Taxes problème
                               'taxes_id' : map_val_default('taxes_id', self.taxes_mapping),
                               'to_weight' : 'to_weight',
                               'type' : 'type',
                               'uom_id/id' : 'uom_id/id',
                               'uom_po_id/id' : 'uom_po_id/id',
                               'weight' : 'weight',
                }
            },
            'product.supplierinfo': { 
                'model' : 'product.supplierinfo',
                'dependencies' : ['product.template'],
                'map' : {
                    'delay' : 'delay',
                    'min_qty' : 'min_qty',
                    'name/id' : 'name/id',
                    'price' : 'price',
                    'product_code' : 'product_code',
                    'product_name' : 'product_name',
                    'product_uom/id' : 'product_uom/id',
                    'date_start' : 'date_start',
                    'date_end' : 'date_end',
                    'product_tmpl_id/id': 'product_tmpl_id/id',
                }
            },
        }
        
        

