# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from erpnext import get_default_company
from wcommerce.utils.customer import WCCustomer


@frappe.whitelist(allow_guest=True)
def create_order(payload, request_id):
    try:
        order_id = payload.get("id")
        if frappe.db.get_value(
            "Sales Order",
            {"wcommerce_order_id": order_id},
        ):
            frappe.db.set_value("WooCommerce Log", request_id, "status", "Skipped")
            return

        customer = WCCustomer(payload.get("customer_id"))
        customer.sync_customer(payload)

        order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer.erpnext_customer,
            "wcommerce_order_id": order_id,
            "company": get_default_company(),
            "posting_date": getdate(
                payload.get("date_created")
            ),
        })
        order.delivery_date = order.posting_date
        for item in payload.get("line_items"):
            item_code = frappe.db.get_value(
                "Item",
                {"wc_product_id": item.get("product_id")},
                "name",
            )
            if not item_code:
                frappe.throw(
                    _("Item not found for product ID: {0}")
                    .format(item.get("product_id"))
                )

            order.append("items", {
                "item_code": item_code,
                "qty": item.get("quantity"),
                "rate": item.get("price"),
            })

        order.flags.ignore_permissions = True
        order.set_missing_values()
        order.insert(ignore_permissions=True)
        frappe.db.set_value("WooCommerce Log", request_id, "status", "Completed")
    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title=("WooCommerce Order Creation Failed"))
        frappe.db.set_value("WooCommerce Log", request_id, {
            "status": "Failed",
            "error": frappe.get_traceback(),
        })
