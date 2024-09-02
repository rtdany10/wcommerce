# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from wcommerce.utils import WooCommerceAPI


class WCProduct(WooCommerceAPI):
    def __init__(self):
        super().__init__()

    def get_product(self, product_id):
        return self.get(f"products/{product_id}")

    def get_products(self, **kwargs):
        return self.get("products", **kwargs)

    def create_product(self):
        if not self.product_data:
            frappe.throw(_("Please generate product data first"))
        return self.post("products", self.product_data)

    def update_product(self, product_id):
        if not self.product_data:
            frappe.throw(_("Please generate product data first"))
        return self.put(f"products/{product_id}", self.product_data)

    def delete_product(self, product_id):
        return self.delete(f"products/{product_id}")

    def generate_product_data(self, product):
        self.product_data = {
            "name": product.item_name,
            "sku": product.name,
            "virtual": product.is_stock_item,
            "type": "simple",
            "description": product.description,
            "short_description": product.get("description"),
        }
        if not product.wc_product_id:
            self.product_data["status"] = "draft"