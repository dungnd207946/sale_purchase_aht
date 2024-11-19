from odoo import api, fields, models
class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Custom Sale Order'
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', store=True, readonly=True)
    @api.model_create_multi
    def create(self, vals_list):
        # Check context để tránh lặp

        if self.env.context.get('from_purchase_order'):
            return super(CustomSaleOrder, self).create(vals_list)
        records = super(CustomSaleOrder, self).create(vals_list)

        # Tạo giá trị cho PurchaseOrder từ thông tin của SaleOrder
        for vals in vals_list:
            # Từ company_id lấy ra partner_id tương ứng, đây là partner_id của Purchase
            # Từ partner_id lấy ra company_id tương ứng, đây là company_id của Sale
            partner_id = vals.get('partner_id')
            purchase_company_id = self.env['res.company'].search([('partner_id', '=', partner_id)], limit=1).id

            company_id = vals.get('company_id')
            purchase_partner_id = self.env['res.company'].search([('id', '=', company_id)], limit=1).partner_id.id

            purchase_order_vals = {
                'partner_id': purchase_partner_id,
                'company_id': purchase_company_id,
                'date_order': fields.Datetime.to_datetime(records.date_order) if records.date_order else fields.Datetime.now(),
                'currency_id': records.currency_id.id,
                # 'order_line': [],  # Dòng đơn hàng sẽ lấy từ Sale Order, nếu cần
                'sale_order_id': records.id,
            }
            # Tạo PurchaseOrder mới từ thông tin lấy được
            purchase_order = self.env['purchase.order'].with_context(from_sale_order=True).sudo().create(purchase_order_vals)
            records.write({'purchase_order_id': purchase_order.id})

            sale_order_lines = records.order_line
            purchase_order_line_vals = []
            for sale_order_line in sale_order_lines:
                purchase_order_line_vals = {
                    'order_id': purchase_order.id,
                    'product_id': sale_order_line.product_id.id,
                    'product_qty': sale_order_line.product_uom_qty,
                    'price_unit': sale_order_line.price_unit,
                    'taxes_id': [(6, 0, sale_order_line.tax_id.ids)],
                    'sale_order_line': sale_order_line.id
                }
                self.env['purchase.order.line'].sudo().create(purchase_order_line_vals)
            # Thêm sudo() để được cấp quyền create (Vì đang ở cty này sẽ không có quyền create ở cty khác)
        return records


    def action_cancel(self):
        print("call first cancel")
        if self.state != 'cancel':
            print('call second cancel')
            c = super(CustomSaleOrder, self).action_cancel()
        purchase_order = (self.env['purchase.order']
                          .with_context(allowed_company_ids=self.env.user.company_ids.ids)
                          .search([('id', '=', self.purchase_order_id.id)], limit=1))
        if purchase_order and purchase_order.state != 'cancel':
            print("Call purchase cancel")
            purchase_order.button_cancel()


