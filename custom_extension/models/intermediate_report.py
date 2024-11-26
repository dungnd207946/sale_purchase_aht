import base64
import io
from datetime import timedelta
import xlsxwriter
from odoo import models, fields, api
from odoo.http import request
class IntermediateReport(models.TransientModel):
    _name = 'intermediate.report'
    _description = 'Intermediate Location Report'

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company, index=True,
        help='Let this field empty if this location is shared between companies')
    location_id = fields.Many2one('stock.location', 'Location')
    last_date = fields.Datetime('End Date', default=fields.Datetime.now, required=True)
    begin_date = fields.Datetime('Begin Date', default=lambda self: fields.Datetime.now() - timedelta(days=7), required=True)

    def compute_line(self):
        products = self.env['product.product'].search([])
        data = []
        i = 0
        for product in products:
            last_available_qty = self.compute_last_available_qty(product)
            last_available_val = self.compute_last_available_val(product, last_available_qty)
            incoming_inter_qty = self.compute_incoming_inter_qty(product)
            incoming_inter_val = self.compute_incoming_inter_val(product, incoming_inter_qty)
            outgoing_inter_qty = self.compute_outgoing_inter_qty(product)
            outgoing_inter_val = self.compute_outgoing_inter_val(product, outgoing_inter_qty)
            begin_available_qty = last_available_qty - incoming_inter_qty + outgoing_inter_qty
            begin_available_val = last_available_val - incoming_inter_val + outgoing_inter_val

            i += 1
            data.append(
                [i, product.default_code, product.name, product.categ_id.complete_name, 'Cái',
                 begin_available_qty, begin_available_val, incoming_inter_qty, incoming_inter_val,
                 outgoing_inter_qty, outgoing_inter_val, last_available_qty, last_available_val]
            )
        return data
    def compute_last_available_qty(self, product):
        current_qty = self.env['stock.quant'].search(
            [('location_id', '=', self.location_id.id), ('product_id', '=', product.id)],
            limit=1).quantity
        incoming_qty = self.env['stock.move.line'].read_group(
            [
                ('location_dest_id', '=', self.location_id.id),
                ('product_id', '=', product.id),
                ('date', '>=', self.last_date),  # Tính từ last_date -> hiện tại
                ('date', '<=', fields.Datetime.now()),
                ('state', '=', 'done')
            ],
            ['product_id', 'quantity:sum'],
            ['product_id']
        )

        outgoing_qty = self.env['stock.move.line'].read_group(
            [
                ('location_id', '=', self.location_id.id),
                ('product_id', '=', product.id),
                ('date', '>=', self.last_date),  # Tính từ last_date -> hiện tại
                ('date', '<=', fields.Datetime.now()),
                ('state', '=', 'done')
            ],
            ['product_id', 'quantity:sum'],
            ['product_id']
        )

        if incoming_qty:
            in_qty = incoming_qty[0]['quantity']
        else:
            in_qty = 0
        if outgoing_qty:
            out_qty = outgoing_qty[0]['quantity']
        else:
            out_qty = 0
        last_available_qty = current_qty - in_qty + out_qty
        return last_available_qty

    def compute_last_available_val(self, product, last_available_qty):
        last_available_val = last_available_qty * product.lst_price
        return last_available_val

    def compute_incoming_inter_qty(self, product):
        incoming_qty = self.env['stock.move.line'].read_group(
            [
                ('location_dest_id', '=', self.location_id.id),
                ('product_id', '=', product.id),
                ('location_usage', 'not in', ['internal', 'transit']),
                ('location_dest_usage', 'in', ['internal', 'transit']),
                ('date', '>=', self.begin_date),  # Tính từ begin_date -> last_date
                ('date', '<=', self.last_date),
                ('state', '=', 'done')
            ],
            ['product_id', 'quantity:sum'],
            ['product_id']
        )

        if incoming_qty:
            return incoming_qty[0]['quantity']
        else:
            return 0

    def compute_incoming_inter_val(self, product, incoming_inter_qty):
        incoming_inter_val = incoming_inter_qty * product.lst_price
        return incoming_inter_val

    def compute_outgoing_inter_qty(self, product):
        outgoing_qty = self.env['stock.move.line'].read_group(
            [
                ('location_id', '=', self.location_id.id),
                ('product_id', '=', product.id),
                ('location_usage', 'in', ['internal', 'transit']),
                ('location_dest_usage', 'not in', ['internal', 'transit']),
                ('date', '>=', self.begin_date),  # Tính từ begin_date -> last_date
                ('date', '<=', self.last_date),
                ('state', '=', 'done')
            ],
            ['product_id', 'quantity:sum'],
            ['product_id']
        )

        if outgoing_qty:
            return outgoing_qty[0]['quantity']
        else:
            return 0

    def compute_outgoing_inter_val(self, product, outgoing_inter_qty):
        outgoing_inter_val = outgoing_inter_qty * product.lst_price
        return outgoing_inter_val


    def show_report(self):
        # Tính toán dữ liệu nhập xuất trước/trong/sau kì
        data = self.compute_line()

        # Tạo file excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Report Sheet')
        title_format = workbook.add_format({'font_name': 'Times New Roman',
                                             'bold': True,
                                             'font_size': 16})
        header_format = workbook.add_format({'font_name': 'Times New Roman',
                                             'bold': True,
                                             'font_size': 12,
                                             'border': 1,
                                             'valign': 'vcenter'})
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

        row = 10
        for line in data:
            worksheet.write_row(row, 0, line, table_format)
            row += 1
        # Tính tổng ở dòng 10 --------------------------------
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
