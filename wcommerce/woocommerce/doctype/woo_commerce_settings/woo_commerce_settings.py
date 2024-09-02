# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from wcommerce.utils import WooCommerceAPI
from frappe.model.document import Document


class WooCommerceSettings(Document):
	def validate(self):
		if not self.enabled:
			return
		self.validate_credentials()

	def validate_credentials(self):
		wcapi = WooCommerceAPI(settings=self)
		try:
			info = wcapi.get("")
			if self.version == info.get("namespace"):
				frappe.msgprint("Connection successful")
			else:
				self.db_set("enabled", 0)
				frappe.msgprint("Connection failed")
		except Exception as e:
			self.db_set("enabled", 0)
			frappe.msgprint(str(e))

