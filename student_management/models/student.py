from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Student(models.Model):
    _name = 'student'
    _description = 'Student'
    code = fields.Char(string='Student code', unique=True, required=True)
    name = fields.Char(string='Student name')
    class_rank = fields.Integer(string='Class rank', compute='_compute_class_rank', store=True)
    school_rank = fields.Integer(string='School rank', compute='_compute_school_rank', store=True)

    classroom_id = fields.Many2one('classroom', string='Class ID')
    school_id = fields.Many2one('school', string='School ID')

    grade_ids = fields.One2many('grade','student_id', string="Grade")

    _sql_constraints = [
        ('unique_grade_student', 'unique(grade_ids)', 'Each student can only have one grade!')
    ]

    @api.model
    def search_student_by_code(self, keyword):
        # Tìm kiếm học sinh có mã số chứa từ khóa
        students = self.search([('code', 'ilike', keyword)])
        return students

    def add_grade(self, math_grade=0, physics_grade=0, chemistry_grade=0):
        total_grade = math_grade + physics_grade + chemistry_grade
        average = total_grade / 3
        return self.env['grade'].create({
            'student_id': self.id,
            'math_grade': math_grade,
            'physics_grade': physics_grade,
            'chemistry_grade': chemistry_grade,
            'total_grade': total_grade,
            'average': average
        })

    def change_grade(self, math_grade, physics_grade, chemistry_grade):
        total_grade = math_grade + physics_grade + chemistry_grade
        average = total_grade / 3
        grade_record = self.grade_ids and self.grade_ids[0] or False
        if grade_record:
            grade_record.write({
                'math_grade': math_grade,
                'physics_grade': physics_grade,
                'chemistry_grade': chemistry_grade,
                'total_grade': total_grade,
                'average': average
            })

    def get_total_grade(self):
        return self.grade_ids and self.grade_ids[0].total_grade or 0

    @api.depends('grade_ids.total_grade', 'school_id', 'classroom_id')
    def _compute_class_rank(self):
        for record in self:
            # Lấy danh sách học sinh trong lớp hiện tại sắp xếp theo total grade
            students = list(record.classroom_id.student_ids.sorted(key=lambda s: s.get_total_grade(), reverse=True))

            # Tạo ra các rank bằng nhau và cộng thêm rank với các học sinh đứng sau
            current_rank = 1
            prev_grade = None
            for i, student in enumerate(students):
                if student.get_total_grade() == prev_grade:
                    student.class_rank = current_rank
                else:
                    student.class_rank = i + 1
                    current_rank = student.class_rank
                prev_grade = student.get_total_grade()

            # Gán class rank của mỗi bản ghi học sinh với vị trí tương ứng của từng người sau khi đã sắp xếp
            record.class_rank = next((student.class_rank for student in students if student == record), -1)

    @api.depends('grade_ids.total_grade')
    def _compute_school_rank(self):
        for record in self:
            students = list(record.school_id.classroom_ids.mapped('student_ids').sorted(
                key=lambda s: s.get_total_grade(),
                reverse=True))
            current_rank = 1
            prev_grade = None
            for i, student in enumerate(students):
                if student.get_total_grade() == prev_grade:
                    student.school_rank = current_rank
                else:
                    student.school_rank = i + 1
                    current_rank = student.school_rank
                prev_grade = student.get_total_grade()
            record.school_rank = next((student.school_rank for student in students if student == record), -1)

    # Reset class khi thay đổi school
    @api.onchange('school_id')
    def _onchange_school_id(self):
        if self.school_id:
            self.classroom_id = False

    # Check class và school khi cập nhật 2 field này
    @api.constrains('classroom_id', 'school_id')
    def _check_classroom_school(self):
        for record in self:
            if record.classroom_id and record.school_id:
                if record.classroom_id.school_id != record.school_id:
                    raise ValidationError(f"The class{record.classroom_id.code} does not belong to school {record.school_id.code}.")
            else:
                raise ValidationError("Both classroom and school must be set.")