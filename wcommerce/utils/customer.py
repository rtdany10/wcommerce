# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from typing import Any, Dict

import frappe
from frappe import _
from frappe.utils import validate_phone_number
from wcommerce.utils import WooCommerceAPI


class WCCustomer(WooCommerceAPI):
    def __init__(self, customer_id: str):
        super().__init__()
        self.customer_id = customer_id
        self.customer_id_field = "wcommerce_customer_id"
        self.erpnext_customer = frappe.db.get_value(
            "Customer", {self.customer_id_field: self.customer_id}
        )

    def is_synced(self) -> bool:
        """Check if customer on Ecommerce site is synced with ERPNext"""
        return bool(self.erpnext_customer)

    def get_customer_doc(self):
        """Get ERPNext customer document."""
        if self.is_synced():
            return frappe.get_last_doc("Customer", {self.customer_id_field: self.customer_id})
        else:
            raise frappe.DoesNotExistError()

    def fetch_and_sync_customer(self):
        """Get customer data from WooCommerce."""
        customer = self.get(f"customers/{self.customer_id}")
        self.sync_customer(customer)

    def sync_customer(self, payload: Dict[str, Any]) -> None:
        customer = payload.get("billing", {})
        if not self.is_synced():
            customer_name = f'{customer.get("first_name")} {customer.get("last_name")}'
            if len(customer_name.strip()) == 0:
                customer_name = customer.get("email")

            _customer = frappe.get_doc(
                {
                    "doctype": "Customer",
                    "name": f"{customer_name}({self.customer_id})",
                    self.customer_id_field: self.customer_id,
                    "customer_name": customer_name,
                    "customer_group": self.settings.customer_group,
                    "territory": self.settings.territory,
                    "customer_type": _("Individual"),
                }
            )

            _customer.flags.ignore_mandatory = True
            _customer.insert(ignore_permissions=True)
            self.erpnext_customer = _customer.name

        if customer:
            self.create_customer_address(
                customer, address_type="Billing"
            )
        if shipping_address := payload.get("shipping", {}):
            self.create_customer_address(
                shipping_address, address_type="Shipping"
            )

    def create_customer_address(
        self,
        address_dict: Dict[str, Any],
        address_type: str = "Billing",
    ) -> None:
        """Create customer address(es) using Customer dict provided by shopify."""
        address_fields = _map_address_fields(address_dict, self.erpnext_customer, address_type)

        frappe.get_doc(
            {
                "doctype": "Address",
                **address_fields,
                "links": [{"link_doctype": "Customer", "link_name": self.erpnext_customer}],
            }
        ).insert(ignore_mandatory=True)

    def _update_existing_address(
        self,
        customer_name,
        address_dict: Dict[str, Any],
        address_type: str = "Billing",
    ) -> None:
        old_address = self.get_customer_address_doc(address_type)

        if not old_address:
            self.create_customer_address(customer_name, address_dict, address_type)
        else:
            exclude_in_update = ["address_title", "address_type"]
            new_values = _map_address_fields(address_dict, customer_name, address_type)

            old_address.update({k: v for k, v in new_values.items() if k not in exclude_in_update})
            old_address.flags.ignore_mandatory = True
            old_address.save()

    def get_customer_address_doc(self, address_type: str):
        try:
            addresses = frappe.get_all("Address", {"link_name": self.erpnext_customer, "address_type": address_type})
            if addresses:
                address = frappe.get_last_doc("Address", {"name": addresses[0].name})
                return address
        except frappe.DoesNotExistError:
            return None


def _map_address_fields(address, customer_name, address_type):
    address_fields = {
        "address_title": customer_name,
        "address_type": address_type,
        "address_line1": address.get("address_1") or "Address 1",
        "address_line2": address.get("address_2"),
        "city": address.get("city"),
        "state": address.get("state"),
        "pincode": address.get("postcode"),
        "email_id": address.get("email"),
    }
    
    country = frappe.db.get_value("Country", {"code": str(address.get("country")).lower()})
    address_fields["country"] = country

    phone = address.get("phone")
    if validate_phone_number(phone, throw=False):
        address_fields["phone"] = phone

    return address_fields
