# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from woocommerce import API


class WooCommerceAPI():
    def __init__(self, settings=None):
        self.settings = settings or frappe.get_single("WooCommerce Settings")
        self.wcapi = API(
            url=self.settings.url,
            consumer_key=self.settings.consumer_key,
            consumer_secret=self.settings.get_password("consumer_password"),
            version=self.settings.version
        )

    def get(self, endpoint, **kwargs):
        return self.wcapi.get(endpoint, **kwargs).json()

    def post(self, endpoint, data, **kwargs):
        return self.wcapi.post(endpoint, data, **kwargs).json()

    def put(self, endpoint, data, **kwargs):
        return self.wcapi.put(endpoint, data, **kwargs).json()
    
    def delete(self, endpoint, **kwargs):
        return self.wcapi.delete(endpoint, **kwargs).json()
