import base64
import io
from datetime import timedelta
import xlsxwriter
from odoo import models, fields, api
from odoo.http import request
class IntermediateReport(models.Model):
    _name = 'intermediate.report'
    _description = 'Intermediate Location Report'

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company, index=True,
        help='Let this field empty if this location is shared between companies')
    location_id = fields.Many2one('stock.location', 'Location')
    last_date = fields.Datetime('End Date', default=fields.Datetime.now, required=True)
    begin_date = fields.Datetime('Begin Date', default=lambda self: fields.Datetime.now() - timedelta(days=7), required=True)
    report_line_ids = fields.One2many('intermediate.report.line', 'report_id')

    def show_report(self):
        products = self.env['product.product'].search([])  # Tìm tất cả sản phẩm

        # Tạo dòng báo cáo cho mỗi sản phẩm
        for product in products:
            line = self.env['intermediate.report.line'].create({
                'report_id': self.id,
                'product_id': product.id,
            })

            # Tự động gọi các hàm compute cho từng dòng báo cáo mới tạo
        i = 0
        data = []
        for line in self.report_line_ids:
            # line._compute_last_available_qty()
            # line._compute_last_available_val()
            #
            # line._compute_incoming_inter_qty()
            # line._compute_incoming_inter_val()
            #
            # line._compute_outgoing_inter_qty()
            # line._compute_outgoing_inter_val()
            #
            # line._compute_begin_available_qty()
            # line._compute_begin_available_val()

            i += 1
            data.append(
                [i, line.product_id.default_code, line.product_id.name, line.product_id.categ_id.complete_name, 'Cái',
                 line.begin_available_qty, line.begin_available_val, line.incoming_inter_qty, line.incoming_inter_val,
                 line.outgoing_inter_qty, line.outgoing_inter_val, line.last_available_qty, line.last_available_val]
            )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Report Sheet')
        title_format = workbook.add_format({'font_name': 'Times New Roman',
                                             'bold': True,
                                             'font_size': 16})
        header_format = workbook.add_format({'font_name': 'Times New Roman',
                                             'bold': True,
                                             'font_size': 12,
                                             'border': 1})
        table_format = workbook.add_format({'font_name': 'Times New Roman',
                                            'font_size': 10,
                                            'border': 1})
        sum_format = workbook.add_format({'font_name': 'Times New Roman',
                                          'bold': True,
                                          'font_size': 10,
                                          'border': 1})
        worksheet.write('A1', 'Company Name: ' + str(self.location_id.company_id.name), title_format)
        worksheet.write('A4', 'BÁO CÁO NHẬP XUẤT TỒN KHO HÀNG HÓA', title_format)
        worksheet.write('A5', f'Từ ngày: {self.begin_date} - Đến ngày: {self.last_date}', title_format)
        worksheet.merge_range('A7:A8', 'STT', header_format)
        worksheet.merge_range('B7:B8', 'Mã hàng', header_format)
        worksheet.merge_range('C7:C8', 'Tên hàng', header_format)
        worksheet.merge_range('D7:D8', 'Nhóm hàng', header_format)
        worksheet.merge_range('E7:E8', 'ĐVT', header_format)
        worksheet.merge_range('F7:G7', 'Số tồn đầu', header_format)
        worksheet.write('F8', 'Số lượng', header_format)
        worksheet.write('G8', 'Giá trị', header_format)
        worksheet.merge_range('H7:I7', 'Nhập trong kỳ', header_format)
        worksheet.write('H8', 'Số lượng', header_format)
        worksheet.write('I8', 'Giá trị', header_format)
        worksheet.merge_range('J7:K7', 'Xuất trong kỳ', header_format)
        worksheet.write('J8', 'Số lượng', header_format)
        worksheet.write('K8', 'Giá trị', header_format)
        worksheet.merge_range('L7:M7', 'Số tồn cuối', header_format)
        worksheet.write('L8', 'Số lượng', header_format)
        worksheet.write('M8', 'Giá trị', header_format)
        worksheet.write('A9', 'A', header_format)
        worksheet.write('B9', 'B', header_format)
        worksheet.write('C9', 'C', header_format)
        worksheet.write('D9', 'D', header_format)
        worksheet.write('E9', 'E', header_format)
        worksheet.write('F9', '(1)', header_format)
        worksheet.write('G9', '(2)', header_format)
        worksheet.write('H9', '(3)', header_format)
        worksheet.write('I9', '(4)', header_format)
        worksheet.write('J9', '(5)', header_format)
        worksheet.write('K9', '(6)', header_format)
        worksheet.write('L9', '(7)=(1)+(3)-(5)', header_format)
        worksheet.write('M9', '(8)=(2)+4-(6)', header_format)
        worksheet.write('A10', str(self.location_id.complete_name), header_format)
        # Tính tổng ở dòng 10 -------------------------------- ?
        row = 10
        for line in data:
            worksheet.write_row(row, 0, line, table_format)
            row += 1
        worksheet.write_formula(9, 5, f'=SUM(F11:F{row})', sum_format)
        worksheet.write_formula(9, 6, f'=SUM(G11:G{row})', sum_format)
        worksheet.write_formula(9, 7, f'=SUM(H11:H{row})', sum_format)
        worksheet.write_formula(9, 8, f'=SUM(I11:I{row})', sum_format)
        worksheet.write_formula(9, 9, f'=SUM(J11:J{row})', sum_format)
        worksheet.write_formula(9, 10, f'=SUM(K11:K{row})', sum_format)
        worksheet.write_formula(9, 11, f'=SUM(L11:L{row})', sum_format)
        worksheet.write_formula(9, 12, f'=SUM(M11:M{row})', sum_format)
        workbook.close()
        output.seek(0)
        excel_file = base64.b64encode(output.read())
        print(excel_file)
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': f'Report Sheet.xlsx',
            'type': 'binary',
            'datas': excel_file,
            'store_fname': f'Report Sheet.xlsx',
            'res_model': 'intermediate.report',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        print(attachment)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
