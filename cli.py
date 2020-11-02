import os
import datetime
import argparse
from data_loader import Nexternal_API

def create_parser():
    parser = argparse.ArgumentParser(
        description="Argument parser for Moondance."
    )
    parser.add_argument(
        "--load-nexternal-orders",
        action="store_true",
        default=False,
        help="Load Nexternal Sales Orders",
    )
    parser.add_argument(
        "--load-nexternal-products",
        action="store_true",
        default=False,
        help="Load Nexternal Products",
    )
    parser.add_argument(
        "--date-range",
        type=str,
        help='Date range to pull in for orders using format "YYYY-MM-DD to YYYY-MM-DD"',
    )

    return parser

def cli():
    parser = create_parser()
    args = parser.parse_args()

    if not args.date_range:
        now = datetime.datetime.now()
        start_date = (now - datetime.timedelta(14))
        end_date = now
    else:
        dates = args.date_range.split(" to ")
        start_date = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(dates[1], "%Y-%m-%d")

    if args.load_nexternal_orders:
        table_name = "sales_orders_nexternal"
        print("{}: starting load for date ranges {} to {}".format(table_name, start_date, end_date))

        api = Nexternal_API(
            data_dir="data",
            table_name=table_name,
            primary_key_list=[
                "order_number",
                "order_line"
            ],
            data_type="sales_orders",
            start_date=start_date,
            end_date=end_date,
            load_method="pk_append"
        )
        api.get_data()
        api.parse_order_data()
        api.load_data()

    if args.load_nexternal_products:
        table_name = "item_master_nexternal"
        print("{}: starting load for date ranges {} to {}".format(table_name, start_date, end_date))

        api = Nexternal_API(
            data_dir="data",
            load_method="product_upsert",
            table_name=table_name,
            primary_key_list=["sku"],
            data_type="products",
            start_date=start_date,
            end_date=end_date
        )
        # api.get_data()
        api.parse_product_data()
        api.load_data()

if __name__ == "__main__":
    cli()