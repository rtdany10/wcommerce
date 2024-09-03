// Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("WooCommerce Log", {
	refresh(frm) {
        if (frm.doc.status == "Failed") {
            frm.add_custom_button(__("Retry"), function() {
                frm.call("retry_sync");
            });
        }
	},
});
