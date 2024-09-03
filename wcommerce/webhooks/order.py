# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from wcommerce.utils.customer import WCCustomer


@frappe.whitelist(allow_guest=True)
def create_order(payload, request_id):
    frappe.set_user("Administrator")
    try:
        order_id = payload.get("id")
        if frappe.db.get_value(
            "Sales Order",
            {"woocommerce_order_id": order_id},
        ):
            frappe.db.set_value("WooCommerce Log", request_id, "status", "Skipped")
            return

        customer = WCCustomer(payload.get("customer_id"))
        customer.sync_customer(payload)

        order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer.erpnext_customer,
        })
        for item in payload.get("line_items"):
            item_code = frappe.db.get_value(
                "Item",
                {"wc_product_id": item.get("product_id")},
                "name",
            )
            order.append("items", {
                "item_code": item_code,
                "qty": item.get("quantity"),
                "rate": item.get("price"),
            })
        order.insert(ignore_permissions=True)
        frappe.db.set_value("WooCommerce Log", request_id, "status", "Completed")
    except Exception as e:
        frappe.db.set_value("WooCommerce Log", request_id, {
            "status": "Failed",
            "error": frappe.get_traceback(),
        })
