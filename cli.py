import os
import datetime
import argparse
import sys
from api_shopify import Shopify_API
from api_amazon import Amazon_API

AMAZON_MARKETPLACE_IDS = "ATVPDKIKX0DER"

def create_parser():
    parser = argparse.ArgumentParser(
        description="Argument parser for Moondance."
    )
    parser.add_argument(
        "--sync-all",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--sync-shopify-products",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--sync-shopify-sales",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--sync-amazon-sales",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--sync-amazon-sales-lines",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--time-interval",
        type=str,
        help='Date range to pull in for orders using format "YYYY-MM-DD to YYYY-MM-DD"',
    )

    return parser

def cli():
    parser = create_parser()
    args = parser.parse_args()
    now = datetime.datetime.utcnow()
    end_datetime = (now - datetime.timedelta(**{"minutes": 3})).isoformat()

    if not args.time_interval:
        start_datetime = (now - datetime.timedelta(**{"days": 3})).isoformat()
    else:
        time_interval = args.time_interval.split(" ")
        interval = {time_interval[1].strip(): int(time_interval[0].strip())}
        print(interval)
        start_datetime = (now - datetime.timedelta(**interval)).isoformat()

    if args.sync_all:
        shopify = Shopify_API(start_datetime)
        shopify.process_data(command="products")
        shopify.process_data(command="sales_orders")

        amazon = Amazon_API()
        amazon.process_data(
            command="sales_order_lines",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
        })
        amazon.process_data(
            command="sales_orders",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
                "LastUpdatedBefore": end_datetime,
                "LastUpdatedAfter": start_datetime,
        })
        sys.exit()

    if args.sync_shopify_products:
        shopify = Shopify_API(start_datetime)
        shopify.process_data(command="products")

    if args.sync_shopify_sales:
        shopify = Shopify_API(start_datetime)
        shopify.process_data(command="sales_orders")

    if args.sync_amazon_sales:
        amazon = Amazon_API()
        amazon.process_data(
            command="sales_orders",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
                "LastUpdatedBefore": end_datetime,
                "LastUpdatedAfter": start_datetime,
        })

    if args.sync_amazon_sales_lines:
        amazon = Amazon_API()
        amazon.process_data(
            command="sales_order_lines",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
        })


if __name__ == "__main__":
    cli()