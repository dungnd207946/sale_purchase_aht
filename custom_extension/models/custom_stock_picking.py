from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        print('Call validate in company ' + str(self.company_id.name))
        res = super(StockPicking, self).button_validate()
        if res == True:
            for picking in self:
                if picking.picking_type_id.code == 'incoming':
                    print("Call purchase validate")
                    for line in picking.move_ids_without_package:
                        # Mỗi move là 1 product
                        quant = self.env['stock.quant'].search([('location_id', '=', 64), ('product_id', '=', line.product_id.id)], limit=1)
                        # Location Intermediate (id = 64)
                        if quant:
                            print(quant.quantity)
                            quant.quantity -= line.quantity
                            print(quant.quantity)
                        else:
                            self.env['stock.quant'].sudo().create({
                                'product_id': line.product_id.id,
                                'location_id': 64,
                                'quantity': -line.quantity,
                            })
                elif picking.picking_type_id.code == 'outgoing':
                    print("Call sale validate")
                    for line in picking.move_ids_without_package:
                        quant = self.env['stock.quant'].search([('location_id', '=', 64), ('product_id', '=', line.product_id.id)], limit=1)
                        if quant:
                            quant.quantity += line.quantity
                        else:
                            self.env['stock.quant'].sudo().create({
                                'product_id': line.product_id.id,
                                'location_id': 64,
                                'quantity': line.quantity,
                            })
                else:
                    print("Internal Transfer !!!")
        return res