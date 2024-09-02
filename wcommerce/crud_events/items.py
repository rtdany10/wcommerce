# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from wcommerce.utils.products import WCProduct


def update_wc_product(doc, method=None):
    wcp = WCProduct()
    wcp.generate_product_data(doc)
    if product_id := doc.get("wc_product_id"):
        wcp.update_product(product_id)
        return

    data = wcp.create_product()
    if data.get("id"):
        doc.db_set("wc_product_id", data.get("id"))
