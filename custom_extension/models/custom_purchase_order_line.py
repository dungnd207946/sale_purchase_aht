from odoo import api, fields, models

class CustomPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Custom Purchase Order Line'
    sale_order_line = fields.Many2one('sale.order.line', string='Sale Order Line', store=True)

    def write(self, vals):
        if self.env.context.get('from_sale_order_line'):
            return super(CustomPurchaseOrderLine, self).write(vals)
        lines = super(CustomPurchaseOrderLine, self).write(vals)
        sale_order_line = self.env['sale.order.line'].sudo().search(['|', ('id', '=', self.sale_order_line.id), ('purchase_order_line', '=', self.id)], limit=1)
        sale_order_line_vals = {}
        if 'product_qty' in vals:
            new_data = {'product_uom_qty': vals['product_qty']}
            sale_order_line_vals = sale_order_line_vals | new_data
        if 'price_unit' in vals:
            new_data = {'price_unit': vals['price_unit']}
            sale_order_line_vals = sale_order_line_vals | new_data
        sale_order_line.with_context(from_purchase_order_line=True).sudo().write(sale_order_line_vals)
        return lines