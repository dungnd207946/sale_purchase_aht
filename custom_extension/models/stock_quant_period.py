from odoo import models, fields, api

class StockQuantPeriod(models.Model):
    _name = 'stock.quant.period'
    _description = 'Stock Quant Period'
    period_time = fields.Datetime(string='Time Each Period', default=fields.Datetime.now)
    location_id = fields.Many2one('stock.location', string='Location')
    quant_period_line_ids = fields.One2many(
        'stock.quant.period.line',
        'stock_quant_period_id',
        string='Stock Quant Period Lines',
    )

    @api.model
    def create_period_record(self):
        location_ids = self.env['stock.quant'].search([]).mapped('location_id')
        print(location_ids)
        for location in location_ids:
            new_period = self.create({'location_id': location.id})
            stock_quants = self.env['stock.quant'].search([('location_id', '=', new_period.location_id.id)])
            for quant in stock_quants:
                self.env['stock.quant.period.line'].create({
                    'stock_quant_period_id': new_period.id,
                    'product_id': quant.product_id.id,
                    'quantity': quant.quantity,
                })