from datetime import timedelta

from odoo import models, fields, api

class IntermediateReportLine(models.Model):
    _name = 'intermediate.report.line'
    _description = 'Intermediate Report Line'

    report_id = fields.Many2one('intermediate.report', 'Report ID', store=True)
    product_id = fields.Many2one('product.product', 'Product', store=True)
    begin_available_qty = fields.Float('Begin Available Quantity', compute='_compute_begin_available_qty', store=True, precompute=True)
    begin_available_val = fields.Float('Begin Available Value', compute='_compute_begin_available_val', store=True, precompute=True)
    incoming_inter_qty = fields.Float('Input Quantity', compute='_compute_incoming_inter_qty', store=True, precompute=True)
    incoming_inter_val = fields.Float('Input Value', compute='_compute_incoming_inter_val', store=True, precompute=True)
    outgoing_inter_qty = fields.Float('Output Quantity', compute='_compute_outgoing_inter_qty', store=True, precompute=True)
    outgoing_inter_val = fields.Float('Output Value', compute='_compute_outgoing_inter_val', store=True, precompute=True)
    last_available_qty = fields.Float('Last Available Quantity', compute='_compute_last_available_qty', store=True, precompute=True)
    last_available_val = fields.Float('Last Available Value', compute='_compute_last_available_val', store=True, precompute=True)

    @api.depends('incoming_inter_qty', 'outgoing_inter_qty', 'last_available_qty')
    def _compute_begin_available_qty(self):
        for record in self:
            record.begin_available_qty = record.last_available_qty - record.incoming_inter_qty + record.outgoing_inter_qty

    @api.depends('incoming_inter_val', 'outgoing_inter_val', 'last_available_val')
    def _compute_begin_available_val(self):
        for record in self:
            record.begin_available_val = record.last_available_val - record.incoming_inter_val + record.outgoing_inter_val

    @api.depends('report_id.begin_date', 'report_id.last_date')
    def _compute_outgoing_inter_qty(self):
        for record in self:
            outgoing_qty = self.env['stock.move.line'].read_group(
                [
                    ('location_id', '=', record.report_id.location_id.id),
                    ('product_id', '=', record.product_id.id),
                    ('location_usage', 'in', ['internal', 'transit']),
                    ('location_dest_usage', 'not in', ['internal', 'transit']),
                    ('date', '>=', record.report_id.begin_date),  # Tính từ begin_date -> last_date
                    ('date', '<=', record.report_id.last_date),
                    ('state', '=', 'done')
                ],
                ['product_id', 'quantity:sum'],
                ['product_id']
            )

            if outgoing_qty:
                record.outgoing_inter_qty = outgoing_qty[0]['quantity']
            else:
                record.outgoing_inter_qty = 0
    @api.depends('outgoing_inter_qty', 'product_id.lst_price')
    def _compute_outgoing_inter_val(self):
        for record in self:
            record.outgoing_inter_val = record.outgoing_inter_qty * record.product_id.lst_price

    @api.depends('report_id.begin_date', 'report_id.last_date')
    def _compute_incoming_inter_qty(self):
        for record in self:
            incoming_qty = self.env['stock.move.line'].read_group(
                [
                    ('location_dest_id', '=', record.report_id.location_id.id),
                    ('product_id', '=', record.product_id.id),
                    ('location_usage', 'not in', ['internal', 'transit']),
                    ('location_dest_usage', 'in', ['internal', 'transit']),
                    ('date', '>=', record.report_id.begin_date),  # Tính từ begin_date -> last_date
                    ('date', '<=', record.report_id.last_date),
                    ('state', '=', 'done')
                ],
                ['product_id', 'quantity:sum'],
                ['product_id']
            )

            if incoming_qty:
                record.incoming_inter_qty = incoming_qty[0]['quantity']
            else:
                record.incoming_inter_qty = 0

    @api.depends('incoming_inter_qty', 'product_id.lst_price')
    def _compute_incoming_inter_val(self):
        for record in self:
            record.incoming_inter_val = record.incoming_inter_qty * record.product_id.lst_price

    @api.depends()
    @api.depends('incoming_inter_qty', 'outgoing_inter_qty', 'report_id.begin_date', 'report_id.last_date')
    def _compute_last_available_qty(self):
        for record in self:
            current_qty = self.env['stock.quant'].search([('location_id', '=', record.report_id.location_id.id), ('product_id', '=', record.product_id.id)], limit=1).quantity
            incoming_qty = self.env['stock.move.line'].read_group(
                [
                    ('location_dest_id', '=', record.report_id.location_id.id),
                    ('product_id', '=', record.product_id.id),
                    ('date', '>=', record.report_id.last_date), # Tính từ last_date -> hiện tại
                    ('date', '<=', fields.Datetime.now()),
                    ('state', '=', 'done')
                ],
                ['product_id', 'quantity:sum'],
                ['product_id']
            )


            outgoing_qty = self.env['stock.move.line'].read_group(
                [
                    ('location_id', '=', record.report_id.location_id.id),
                    ('product_id', '=', record.product_id.id),
                    ('date', '>=', record.report_id.last_date), # Tính từ last_date -> hiện tại
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
            record.last_available_qty = current_qty - in_qty + out_qty

    @api.depends('last_available_qty', 'product_id.lst_price')
    def _compute_last_available_val(self):
        for record in self:
            record.last_available_val = record.last_available_qty * record.product_id.lst_price