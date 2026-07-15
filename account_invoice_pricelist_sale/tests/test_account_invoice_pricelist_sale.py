# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.account_invoice_pricelist.tests.test_account_move_pricelist import (
    TestAccountMovePricelist,
)


class TestAccountInvoicePricelistSale(TestAccountMovePricelist):
    def test_invoice_create_from_sale(self):
        # --- FIX PARA ODOO 19: Asignar cuentas e impuestos obligatorios ---
        income_account = self.env['account.account'].search([
            ('company_ids', 'in', self.env.company.id),
            ('account_type', '=', 'income')
        ], limit=1)
        
        if income_account:
            self.product_product.property_account_income_id = income_account.id
            self.product_product.property_account_expense_id = income_account.id
            
        tax = self.env['account.tax'].search([
            ('company_id', '=', self.env.company.id),
            ('type_tax_use', '=', 'sale')
        ], limit=1)
        
        if tax:
            self.product_product.taxes_id = [Command.set([tax.id])]
        # ------------------------------------------------------------------

        # Create Sale Order
        self.product_product.invoice_policy = "order"
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.sale_pricelist3.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product_product.name,
                            "product_id": self.product_product.id,
                            "product_uom_qty": 5,
                            "product_uom_id": self.product_product.uom_id.id,
                            "price_unit": self.product_product.list_price,
                            "qty_delivered": 5,
                        }
                    )
                ],
            }
        )

        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(
            invoice.pricelist_id,
            order.pricelist_id,
            "Invoice Pricelist has not been recovered from sale order",
        )
