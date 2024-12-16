from odoo import models, fields

class Classroom(models.Model):
    _name = 'classroom'
    _description = 'Classroom'
    code = fields.Char(string='Class code', required=True)
    name = fields.Char(string='Class name')
    school_id = fields.Many2one('school', string='School ID', ondelete='cascade')
    student_ids = fields.One2many('student', 'classroom_id', string='Students')

