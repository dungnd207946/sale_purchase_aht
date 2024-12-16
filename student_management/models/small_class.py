from odoo import models, fields

class SmallClass(models.Model):
    _name = 'small_class'
    _inherit = 'classroom'

    note = fields.Char(string='Class note')