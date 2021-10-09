import os
import io
import time
from dotenv import load_dotenv
from sp_api.api import (
    Inventories,
    ListingsItems,
    Orders,
    Reports,
    Feeds,
    Catalog,
    Finances,
)
from sp_api.base import SellingApiException
from sp_api.base.reportTypes import ReportType
from datetime import datetime, timedelta

load_dotenv()


#         CreatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat()
AMAZON_SELLER_ID = os.environ.get("AMAZON_SELLER_ID")
CHECK_INTERVAL = 30
AMAZON_MARKETPLACE_IDS = ["ATVPDKIKX0DER"]


class Amazon_Report(object):
    def __init__(self, report_type, file_name):
        self.file_name = file_name
        self.report_type = report_type
        self.report_id = None
        self.document_id = None

        self.create_report()

        if self.report_id:
            while not self.document_id:
                time.sleep(CHECK_INTERVAL)
                self.get_report()

        if self.document_id != -1:
            self.download_report()

    def create_report(self):
        try:
            res = Reports().create_report(reportType=self.report_type)
            self.report_id = res.payload["reportId"]
            print("{} report id created".format(self.report_id))
        except SellingApiException as ex:
            print(ex)

    def get_report(self):
        try:
            res = Reports().get_report(report_id=self.report_id)
            data = res.payload

            if data["processingStatus"] in ("IN_QUEUE", "IN_PROGRESS"):
                print(
                    "{} report not ready, status is {} checking again in {} seconds".format(
                        self.report_type,
                        data["processingStatus"],
                        CHECK_INTERVAL,
                    )
                )
            elif data["processingStatus"] == "DONE":
                print("{} report has been completed".format(self.report_type))
                self.document_id = data["reportDocumentId"]
            else:
                print("{} report has NOT been completed".format(self.report_type))
                print(data)
                self.document_id = -1
        except SellingApiException as ex:
            print(ex)

    def download_report(self):
        try:
            res = Reports().get_report_document(
                document_id=self.document_id,
                decrypt=True,
            )
            with io.open(self.file_name, "w", encoding="utf-8") as w:
                print(res.payload["document"])
                w.write(res.payload["document"])
                print(
                    "{} report downloaded and written to file {}".format(
                        self.report_type, self.file_name
                    )
                )
        except SellingApiException as ex:
            print(ex)


# report_type = "GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING"
# file_name = f"{report_type}.tsv"
# report = Amazon_Report(
#     report_type=report_type,
#     file_name=file_name,
# )
patches = {
    "productType": "PRODUCT",
    "patches": [
        {
            "op": "replace",
            "path": "/attributes/fulfillment_availability",
            "value": [{"fulfillment_channel_code": "DEFAULT", "quantity": 1}],
        }
    ],
}


try:
    res = ListingsItems().patch_listings_item(
        sellerId=AMAZON_SELLER_ID,
        sku="CONC-LAV-8",
        marketplaceIds=AMAZON_MARKETPLACE_IDS,
        body=patches,
    )
    print(res.payload)  # json data
except SellingApiException as ex:
    print(ex)

# res = FbaInboundEligibility().get_item_eligibility_preview()
# print(res.payload["document"])
# CreatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat()

# ReportType.GET_V2_SELLER_PERFORMANCE_REPORT
# ReportType.GET_FLAT_FILE_OPEN_LISTINGS_DATA
# ReportType.GET_MERCHANT_LISTINGS_ALL_DATA
# ReportType.GET_MERCHANT_LISTINGS_DATA
# ReportType.GET_MERCHANT_LISTINGS_INACTIVE_DATA
# ReportType.GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT
# ReportType.GET_MERCHANT_LISTINGS_DATA_LITE
# ReportType.GET_MERCHANT_LISTINGS_DATA_LITER
# ReportType.GET_MERCHANT_CANCELLED_LISTINGS_DATA
# ReportType.GET_MERCHANT_LISTINGS_DEFECT_DATA
# ReportType.GET_PAN_EU_OFFER_STATUS
# ReportType.GET_MFN_PAN_EU_OFFER_STATUS
# ReportType.GET_FLAT_FILE_GEO_OPPORTUNITIES
# ReportType.GET_REFERRAL_FEE_PREVIEW_REPORT
# ReportType.GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING
# ReportType.GET_ORDER_REPORT_DATA_INVOICING
# ReportType.GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING
# ReportType.GET_ORDER_REPORT_DATA_TAX
# ReportType.GET_FLAT_FILE_ORDER_REPORT_DATA_TAX
# ReportType.GET_ORDER_REPORT_DATA_SHIPPING
# ReportType.GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING
# ReportType.GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL
# ReportType.GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL
# ReportType.GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE
# ReportType.GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL
# ReportType.GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL
# ReportType.GET_FLAT_FILE_PENDING_ORDERS_DATA
# ReportType.GET_PENDING_ORDERS_DATA
# ReportType.GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA
# ReportType.GET_XML_RETURNS_DATA_BY_RETURN_DATE
# ReportType.GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE
# ReportType.GET_XML_MFN_PRIME_RETURNS_REPORT
# ReportType.GET_CSV_MFN_PRIME_RETURNS_REPORT
# ReportType.GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT
# ReportType.GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT
# ReportType.GET_SELLER_FEEDBACK_DATA
# ReportType.GET_V1_SELLER_PERFORMANCE_REPORT
# ReportType.GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE
# ReportType.GET_V2_SETTLEMENT_REPORT_DATA_XML
# ReportType.GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2
# ReportType.GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL
# ReportType.GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING
# ReportType.GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX
# ReportType.GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA
# ReportType.GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA
# ReportType.GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA
# ReportType.GET_REMOTE_FULFILLMENT_ELIGIBILITY
# ReportType.GET_AFN_INVENTORY_DATA
# ReportType.GET_AFN_INVENTORY_DATA_BY_COUNTRY
# ReportType.GET_LEDGER_SUMMARY_VIEW_DATA
# ReportType.GET_LEDGER_DETAIL_VIEW_DATA
# ReportType.GET_FBA_FULFILLMENT_CURRENT_INVENTORY_DATA
# ReportType.GET_FBA_FULFILLMENT_MONTHLY_INVENTORY_DATA
# ReportType.GET_FBA_FULFILLMENT_INVENTORY_RECEIPTS_DATA
# ReportType.GET_RESERVED_INVENTORY_DATA
# ReportType.GET_FBA_FULFILLMENT_INVENTORY_SUMMARY_DATA
# ReportType.GET_FBA_FULFILLMENT_INVENTORY_ADJUSTMENTS_DATA
# ReportType.GET_FBA_FULFILLMENT_INVENTORY_HEALTH_DATA
# ReportType.GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA
# ReportType.GET_FBA_MYI_ALL_INVENTORY_DATA
# ReportType.GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT
# ReportType.GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA
# ReportType.GET_STRANDED_INVENTORY_UI_DATA
# ReportType.GET_STRANDED_INVENTORY_LOADER_DATA
# ReportType.POST_FLAT_FILE_INVLOADER_DATA
# ReportType.GET_FBA_INVENTORY_AGED_DATA
# ReportType.GET_EXCESS_INVENTORY_DATA
# ReportType.GET_FBA_STORAGE_FEE_CHARGES_DATA
# ReportType.GET_PRODUCT_EXCHANGE_DATA
# ReportType.GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA
# ReportType.GET_FBA_REIMBURSEMENTS_DATA
# ReportType.GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA
# ReportType.GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA
# ReportType.GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA
# ReportType.GET_FBA_RECOMMENDED_REMOVAL_DATA
# ReportType.GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA
# ReportType.GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA
# ReportType.GET_FBA_UNO_INVENTORY_DATA
# ReportType.GET_FLAT_FILE_SALES_TAX_DATA
# ReportType.SC_VAT_TAX_REPORT
# ReportType.GET_VAT_TRANSACTION_DATA
# ReportType.GET_GST_MTR_B2B_CUSTOM
# ReportType.GET_GST_MTR_B2C_CUSTOM
# ReportType.GET_XML_BROWSE_TREE_DATA
# ReportType.GET_EASYSHIP_DOCUMENTS
# ReportType.GET_EASYSHIP_PICKEDUP
# ReportType.GET_EASYSHIP_WAITING_FOR_PICKUP
# ReportType.RFQD_BULK_DOWNLOAD
# ReportType.FEE_DISCOUNTS_REPORT
# ReportType.GET_FLAT_FILE_OFFAMAZONPAYMENTS_SANDBOX_SETTLEMENT_DATA
