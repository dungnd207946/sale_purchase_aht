from odoo import api, fields, models

class CustomSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = "Custom Sale Order Line"
    purchase_order_line = fields.Many2one('purchase.order.line', string="Purchase Order Line", store=True)

    def write(self, vals):
        print('Call update sale line')
        if self.env.context.get('from_purchase_order_line'):
            return super(CustomSaleOrderLine, self).write(vals)
        lines = super(CustomSaleOrderLine, self).write(vals)
        purchase_order_line = self.env['purchase.order.line'].sudo().search(['|', ('id', '=', self.purchase_order_line.id), ('sale_order_line', '=', self.id)], limit=1)
        if purchase_order_line:
            print('Found purchase line')
        else:
            print('not found')
        purchase_order_line_vals = {}
        if 'product_uom_qty' in vals:
            new_data = {'product_qty': vals['product_uom_qty']}
            purchase_order_line_vals = purchase_order_line_vals | new_data
        if 'price_unit' in vals:
            new_data = {'price_unit': vals['price_unit']}
            purchase_order_line_vals = purchase_order_line_vals | new_data
        purchase_order_line.with_context(from_sale_order_line=True).sudo().write(purchase_order_line_vals)
        return lines
