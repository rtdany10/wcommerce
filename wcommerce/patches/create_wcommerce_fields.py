# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Item": [
				{
					"fieldname": "wc_product_id",
					"label": "WooCommerce Product ID",
					"fieldtype": "Data",
					"insert_after": "stock_uom",
					"read_only": 1,
					"unique": 1,
				},
			],
			"Customer": [
				{
					"fieldname": "wcommerce_customer_id",
					"label": "WooCommerce Customer ID",
					"fieldtype": "Data",
					"read_only": 1,
					"insert_after": "customer_name",
					"unique": 1,
				},
			],
			"Sales Order": [
				{
					"fieldname": "wcommerce_order_id",
					"label": "WooCommerce Order ID",
					"fieldtype": "Data",
					"insert_after": "customer",
					"read_only": 1,
					"unique": 1,
				},
			],
		}
	)