from odoo import models, fields, api

class StockQuantPeriodLine(models.Model):
    _name = 'stock.quant.period.line'
    _description = 'Stock Quant Period Line'
    stock_quant_period_id = fields.Many2one('stock.quant.period', string='Stock Quant Period')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)

