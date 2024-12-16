from odoo import models, fields, api

class StudentSearchWizard(models.TransientModel):
    _name = 'student.search.wizard'
    _description = 'Student Search Wizard'

    keyword = fields.Char(string="Student code")
    result_ids = fields.Many2many('student', string="Search Results")

    def action_search(self):
        # Gọi phương thức search_student_by_code để tìm kiếm
        students = self.env['student'].search_student_by_code(self.keyword)
        self.result_ids = students

        # Mở lại wizard để hiển thị kết quả
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'student.search.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
