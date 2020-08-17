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
        "--date-range",
        type=str,
        help='Date range to pull in for orders using format "YYYY-MM-DD to YYYY-MM-DD"',
    )

    return parser

def cli():
    parser = create_parser()
    args = parser.parse_args()

    if args.load_nexternal_orders:
        date_range = args.date_range
        data_dir = "data"

        if not date_range:
            start_date = (datetime.datetime.now() - datetime.timedelta(3)).strftime("%m/%d/%Y")
            end_date = datetime.datetime.now().strftime("%m/%d/%Y")
        else:
            dates = date_range.split(" to ")
            start_date = datetime.datetime.strptime(dates[0], "%Y-%m-%d").strftime("%m/%d/%Y")
            end_date = datetime.datetime.strptime(dates[1], "%Y-%m-%d").strftime("%m/%d/%Y")
        
        print("Nexternal Orders: starting load for date ranges {} to {}".format(start_date, end_date))

        api = Nexternal_API(data_dir=data_dir)
        api.get_order_data(start_date=start_date, end_date=end_date)
        api.merge_order_data()
        api.load_order_data()


if __name__ == "__main__":
    cli()