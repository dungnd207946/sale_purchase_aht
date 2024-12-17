from odoo import models, fields, api

class StateInModel(models.Model):
    _name = 'state.in.model'
    _description = "State in certain Model"
    name = fields.Char(string='State')
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', store=True, required=True)

