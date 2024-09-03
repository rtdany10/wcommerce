# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from frappe.model.document import Document
from wcommerce.webhooks import EVENT_MAPPER


class WooCommerceLog(Document):
	@frappe.whitelist()
	def retry_sync(self):
		if self.status != "Failed":
			frappe.throw(_("Only failed logs can be retried."))

		frappe.enqueue(
			method=EVENT_MAPPER[self.event],
			queue="short",
			timeout=300,
			is_async=True,
			**{"payload": json.loads(self.request_data), "request_id": self.name},
		)
		frappe.msgprint(_("Sync has been enqueued."))
