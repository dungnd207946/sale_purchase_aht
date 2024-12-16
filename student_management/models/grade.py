from odoo import models, fields, api

class Grade(models.Model):
    _name = 'grade'
    _description = 'Grade'

    student_id = fields.Many2one('student', string="Student", ondelete='cascade', unique=True)
    math_grade = fields.Float(string="Math Grade")
    physics_grade = fields.Float(string="Physics Grade")
    chemistry_grade = fields.Float(string="Chemistry Grade")
    total_grade = fields.Float(string="Total Grade", compute='_compute_total_grade', store=True)
    average = fields.Float(string="Average", compute='_compute_average', store=True)

    _sql_constraints = [
        ('unique_student_grade', 'unique(student_id)', 'Each student can only have one grade!')
    ]
    @api.depends('math_grade', 'physics_grade', 'chemistry_grade')
    def _compute_total_grade(self):
        for record in self:
            record.total_grade = record.math_grade + record.physics_grade + record.chemistry_grade

    @api.depends('total_grade')
    def _compute_average(self):
        for record in self:
            record.average = record.total_grade / 3 if record.total_grade else 0