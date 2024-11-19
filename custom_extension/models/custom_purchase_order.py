from odoo import api, fields, models

class CustomPurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Custom Purchase Order'
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', store=True, readonly=True)
    @api.model_create_multi
    def create(self, vals_list):
        # Check context để tránh lặp
        if self.env.context.get('from_sale_order'):
            return super(CustomPurchaseOrder, self).create(vals_list)
        records = super(CustomPurchaseOrder, self).create(vals_list)

        for vals in vals_list:
            partner_id = vals.get('partner_id')
            sale_company_id = self.env['res.company'].search([('partner_id', '=', partner_id)], limit=1).id
            company_id = vals.get('company_id')
            sale_partner_id = self.env['res.company'].search([('id', '=', company_id)], limit=1).partner_id.id

            sale_order_vals = {
                'partner_id': sale_partner_id,
                'company_id': sale_company_id,
                'date_order': fields.Datetime.to_datetime(records.date_order) if records.date_order else fields.Datetime.now(),
                'currency_id': records.currency_id.id,
                'purchase_order_id': records.id,
            }
            sale_order = self.env['sale.order'].with_context(from_purchase_order=True).sudo().create(sale_order_vals)
            records.write({'sale_order_id': sale_order.id})

            purchase_order_lines = records.order_line
            for purchase_order_line in purchase_order_lines:
                sale_order_line_vals = {
                    'order_id': sale_order.id,
                    'product_id': purchase_order_line.product_id.id,
                    'product_uom_qty': purchase_order_line.product_qty,
                    'price_unit': purchase_order_line.price_unit,
                    'tax_id': [(6, 0, purchase_order_line.taxes_id.ids)], # Trong sale là tax_id, trong purchase là taxes_id
                    'purchase_order_line': purchase_order_line.id
                }
                print('add purchase line in sale')
                print(sale_order_line_vals['purchase_order_line'])
                self.env['sale.order.line'].sudo().create(sale_order_line_vals)
        return records

    def button_cancel(self):
        if self.state != 'cancel':
            super(CustomPurchaseOrder, self).button_cancel()
            sale_order = self.env['sale.order'].with_context(allowed_company_ids=self.env.user.company_ids.ids).search([('id', '=', self.sale_order_id.id)], limit=1)
            if sale_order and sale_order.state != 'cancel':
                sale_order.action_cancel()

    # def write(self, vals):
    #     if self.env.context.get('from_sale_order'):
    #         return super(CustomPurchaseOrder, self).write(vals)
    #     super(CustomPurchaseOrder, self).write(vals)
    #     print("Call write in class CustomPurchase")
    #     print(vals)
    #     print(self.partner_id.id)
    #     print(self.company_id.id)
    #
    #     partner_id = self.partner_id.id
    #     sale_company = self.env['res.company'].search([('partner_id', '=', partner_id)], limit=1)
    #     sale_company.write(vals)
    #
    #     sale_order_line = self.env['sale.order.line'].search([('order_id', '=', self.sale_order_id.id)])
    #     for line in sale_order_line:
    #
    #     sale_order_line_vals = {
    #         'product_uom_qty':
    #
    #     }
    #     return True