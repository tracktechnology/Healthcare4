import frappe
# import erpnext
from healthcare.healthcare.doctype.healthcare_settings.healthcare_settings import get_account
from frappe.utils import flt, get_link_to_form, now_datetime, nowdate, nowtime
# from erpnext.stock.stock_ledger import get_valuation_rate
# from frappe.query_builder.functions import Sum


# @frappe.whitelist
def make_stock_entry(items_doc_type,items_doc_name, stock_entry_type, from_warehouse=None, to_warehouse=None,
                     company="Track INT'l Trad (Demo)",posting_date=None,posting_time=None,allow_draft=True):
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry = set_stock_items(stock_entry, items_doc_name, items_doc_type)
    if not stock_entry: return None
    stock_entry.stock_entry_type = stock_entry_type
    stock_entry.from_warehouse = from_warehouse
    stock_entry.to_warehouse = to_warehouse
    stock_entry.company = company
    expense_account = get_account(None, "expense_account", "Healthcare Settings", company)
    cost_center = frappe.get_cached_value("Company", company, "cost_center")
    items_display = []
    for item_line in stock_entry.items:
        # cost_center = frappe.get_cached_value("Company", company, "cost_center")
        item_line.cost_center = cost_center
        item_line.expense_account = expense_account
        # item_line.valuation_rate = get_basic_rate(item_line.item_code,stock_entry)
        items_display.append(str(item_line.as_dict()))

    # frappe.throw(str(items_display))
    if posting_date:
        stock_entry.posting_date = posting_date
        stock_entry.set_posting_time = 1
    if posting_time:
        stock_entry.posting_time = posting_time
    stock_entry.save(ignore_permissions=True)
    if stock_entry.check_balance_before_submit():
        stock_entry.submit()
    elif allow_draft:
        # TODO: print all required items
        frappe.msgprint(str(from_warehouse) + "  need restocking")
    else:
        frappe.throw(str(from_warehouse) + "  need restocking")
    return stock_entry.name


@frappe.whitelist()
def make_stock_entry_materail_consumption(items_doc_type,items_doc_name, from_warehouse):
    # frappe.throw(str(from_warehouse))
    return make_stock_entry(items_doc_type,items_doc_name, "Material Issue", from_warehouse=from_warehouse)


@frappe.whitelist()
def set_stock_items(doc, stock_detail_parent, parenttype):
    items = get_items("Clinical Procedure Item", stock_detail_parent, parenttype)
    if not items:
        # frappe.msgprint("No Items for consumption")
        return None
    for item in items:
        # frappe.throw(str(item))
        se_child = doc.append("items")
        se_child.item_code = item.item_code
        se_child.item_name = item.item_name
        se_child.uom = item.uom
        se_child.stock_uom = item.stock_uom
        se_child.qty = flt(item.qty)
        # in stock uom
        se_child.transfer_qty = flt(item.transfer_qty)
        se_child.conversion_factor = flt(item.conversion_factor)
        if item.batch_no:
            se_child.batch_no = item.batch_no
        if parenttype == "Clinical Procedure Template":
            se_child.invoice_separately_as_consumables = item.invoice_separately_as_consumables
        # frappe.throw(str(se_child.as_dict()))

    return doc


def get_items(table, parent, parenttype):
    items = frappe.db.get_all(
        table, filters={"parent": parent, "parenttype": parenttype}, fields=["*"]
    )

    return items

#
# def get_basic_rate(item_code,self):
#     table = frappe.qb.DocType("Stock Ledger Entry")
#     query = (
#         frappe.qb.from_(table)
#         .select(Sum(table.stock_value_difference) / Sum(table.actual_qty))
#         .where(
#             (table.item_code == item_code)
#             & (table.is_cancelled == 0)
#         )
#     )
#
#     last_valuation_rate = query.run()
#     frappe.throw(str(item_code) + "  ::::: " +  str(last_valuation_rate))
#     if last_valuation_rate:
#         return flt(last_valuation_rate[0][0])
#     return 0.0
#     # basic_rate = get_valuation_rate(
#     #     item_code,
#     #     self.from_warehouse,
#     #     self.doctype,
#     #     self.name,
#     #     0,
#     #     currency=erpnext.get_company_currency(self.company),
#     #     company=self.company,
#     # )
#     # return basic_rate