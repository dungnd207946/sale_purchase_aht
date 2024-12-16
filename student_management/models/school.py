from odoo import models, fields

class School(models.Model):
    _name = 'school'
    _description = 'School Management'
    code = fields.Char(string='School Code', unique=True, required=True)
    name = fields.Char(string='School name')
    classroom_ids = fields.One2many('classroom', 'school_id', string='Class ID')

    def add_class(self, name, code):
        return self.env['classroom'].create({'name': name, 'code': code, 'school_id': self.id})

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}"  # Hiển thị dạng "[code] name"
            result.append((record.id, name))
        return result

