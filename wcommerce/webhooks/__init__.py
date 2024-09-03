# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
import hmac
import json
import base64
import hashlib
from frappe import _


EVENT_MAPPER = {
	"order.updated": "wcommerce.webhooks.order.create_order",
	"order.created": "wcommerce.webhooks.order.create_order",
}


@frappe.whitelist(allow_guest=True)
def store_request_data() -> None:
	if frappe.request:
		hmac_header = frappe.get_request_header("X-WC-Webhook-Signature")
		if not hmac_header:
			return {}

		if not _validate_request(frappe.request, hmac_header):
			return {}

		data = json.loads(frappe.request.data)
		event = frappe.request.headers.get("X-WC-Webhook-Topic")

		process_request(data, event)

	return {}


def process_request(data, event):
	# create log
	log = create_wcommerce_log(event=event, request_data=data)

	# enqueue backround job
	frappe.enqueue(
		method=EVENT_MAPPER[event],
		queue="short",
		timeout=300,
		is_async=True,
		**{"payload": data, "request_id": log.name},
	)


def _validate_request(req, hmac_header):
	settings = frappe.get_single("WooCommerce Settings")
	secret_key = settings.get_password("consumer_password")

	sig = base64.b64encode(hmac.new(secret_key.encode("utf8"), req.data, hashlib.sha256).digest())

	if sig != bytes(hmac_header.encode()):
		frappe.log_error(title=f"verification failed-{bytes(hmac_header.encode())}<==>{sig}", message=str(req.data))
		frappe.msgprint(_("Unverified Webhook Data"))
		return False

	return True


def create_wcommerce_log(event, request_data):
	log = frappe.get_doc(
		{
			"doctype": "WooCommerce Log",
			"event": event,
			"status": "Pending",
			"request_data": pretty_json(request_data),
		}
	)
	log.insert(ignore_permissions=True)
	return log


def pretty_json(obj):
    if not obj:
        return ""

    if isinstance(obj, str):
        return obj

    return frappe.as_json(obj, indent=4)