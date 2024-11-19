from odoo import api, fields, models

class CustomMassCancelOrders(models.TransientModel):
    _inherit = 'sale.mass.cancel.orders'

    def action_mass_cancel(self):
        print("Call mass cancel")
        super(CustomMassCancelOrders, self).action_mass_cancel()
        for sale_order in self.sale_order_ids:
            sale_order.action_cancel()