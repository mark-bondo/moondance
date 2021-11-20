import os
import datetime
import argparse
import sys
import logging
import contextlib
import psycopg2
from dotenv import load_dotenv
from logging.config import dictConfig
from api_shopify import Shopify_API
from api_amazon import Amazon_API

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {"format": "%(levelname)s\t%(name)s\t%(asctime)s\t%(module)s@%(lineno)s\t%(message)s"},
    },
    "handlers": {
        "cli_handler": {
            "level": "INFO",
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "formatter": "simple",
            "filename": "automationtools/logs/cli.log",
            "maxBytes": 1000000,
            "backupCount": 10,
            "encoding": "utf8",
        }
    },
    "loggers": {
        "cli_logger": {"level": "INFO", "handlers": ["cli_handler"]},
    },
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("cli_logger")

AMAZON_MARKETPLACE_IDS = "ATVPDKIKX0DER"
DB_STRING = os.getenv("DB_STRING")


def create_parser():
    parser = argparse.ArgumentParser(description="Argument parser for Moondance.")
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
        "--sync-shopify-order-events",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--sync-shopify-customers",
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
        "--sync-amazon-financial-events",
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
        help="format is {number} {time_period}, e.g., 5 days, 3 years, etc",
    )
    parser.add_argument(
        "--date-range",
        type=str,
        help='Date range to pull in for orders using format "YYYY-MM-DD to YYYY-MM-DD"',
    )
    parser.add_argument(
        "--rebuild-sales-orders",
        action="store_true",
        default=False,
    )

    return parser


def cli():
    parser = create_parser()
    args = parser.parse_args()

    if args.date_range:
        date_range = [
            datetime.datetime.strptime(x.strip(), "%Y-%m-%d").isoformat()
            for x in args.date_range.lower().split(" to ")
        ]

        interval = {
            "start_datetime": date_range[0],
            "end_datetime": date_range[1],
        }
    else:
        interval = set_interval(args.time_interval)

    if args.sync_all:
        sync_shopify(
            command="products",
            request_parameters={
                "updated_at_min": interval["start_datetime"],
                "limit": 100,
            },
        )

        sync_shopify(
            command="sales_orders",
            request_parameters={
                "updated_at_min": interval["start_datetime"],
                "status": "any",
                "limit": 100,
            },
        )

        sync_shopify(
            command="sync_shopify_order_events",
            request_parameters={
                "limit": 100,
            },
        )

        sync_shopify(
            command="customers",
            request_parameters={
                "updated_at_min": interval["start_datetime"],
                "limit": 100,
            },
        )

        sync_amazon(
            command="sales_orders",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
                "LastUpdatedBefore": interval["end_datetime"],
                "LastUpdatedAfter": interval["start_datetime"],
            },
        )

        sync_amazon(
            command="sales_order_lines",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
                "LastUpdatedBefore": interval["end_datetime"],
                "LastUpdatedAfter": interval["start_datetime"],
            },
        )

        sync_amazon(
            command="financial_events",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
                "PostedBefore": interval["end_datetime"],
                "PostedAfter": interval["start_datetime"],
            },
        )

        rebuild_sales_orders()

        sys.exit()

    if args.sync_shopify_products:
        sync_shopify(
            command="products",
            request_parameters={
                "updated_at_min": interval["start_datetime"],
            },
        )

    if args.sync_shopify_sales:
        sync_shopify(
            command="sales_orders",
            request_parameters={
                "status": "any",
                "updated_at_min": interval["start_datetime"],
                "limit": 100,
            },
        )

    if args.sync_shopify_order_events:
        sync_shopify(
            command="sync_shopify_order_events",
            request_parameters={
                "limit": 100,
            },
        )

    if args.sync_shopify_customers:
        sync_shopify(
            command="customers",
            request_parameters={
                "updated_at_min": interval["start_datetime"],
                "limit": 100,
            },
        )

    if args.sync_amazon_sales:
        sync_amazon(
            command="sales_orders",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
                "LastUpdatedBefore": interval["end_datetime"],
                "LastUpdatedAfter": interval["start_datetime"],
            },
        )

    if args.sync_amazon_sales_lines:
        sync_amazon(
            command="sales_order_lines",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
                # "LastUpdatedBefore": interval["end_datetime"],
                # "LastUpdatedAfter": interval["start_datetime"],
            },
        )

    if args.sync_amazon_financial_events:
        sync_amazon(
            command="financial_events",
            request_parameters={
                "MarketplaceIds": AMAZON_MARKETPLACE_IDS,
                "PostedBefore": interval["end_datetime"],
                "PostedAfter": interval["start_datetime"],
            },
        )

    if args.rebuild_sales_orders:
        rebuild_sales_orders()


def set_interval(time_interval):
    try:
        log = "set time interval:  starting"
        logger.info(log)

        now = datetime.datetime.utcnow()
        end_datetime = (now - datetime.timedelta(**{"minutes": 3})).isoformat()

        if not time_interval:
            start_datetime = (now - datetime.timedelta(**{"days": 3})).isoformat()
        else:
            time_interval = time_interval.split(" ")
            interval = {time_interval[1].strip(): int(time_interval[0].strip())}
            start_datetime = (now - datetime.timedelta(**interval)).isoformat()

        return {
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
        }
    except Exception:
        log = "set time interval: failed"
        logger.error(log, exc_info=1)
        sys.exit()
    finally:
        log = f"set time interval:  completed using range of {start_datetime} to {end_datetime}"
        logger.info(log)


def sync_shopify(command, request_parameters):
    try:
        logger.info(f"sync shopify {command}: starting program")
        shopify = Shopify_API(logger=logger)
        shopify.process_data(command=command, request_parameters=request_parameters)
        logger.info(f"sync shopify {command}: completed program")
    except Exception:
        logger.error(f"sync shopify {command}: failed program", exc_info=1)


def sync_amazon(command, request_parameters):
    try:
        logger.info(f"sync amazon {command}: starting program")
        amazon = Amazon_API(logger=logger)
        amazon.process_data(command=command, request_parameters=request_parameters)
        logger.info(f"sync amazon {command}: completed program")
    except Exception:
        logger.error(f"sync amazon {command}: failed program", exc_info=1)


def rebuild_sales_orders():
    try:
        logger.info("rebuilding sales orders: starting program")
        script_path = "automationtools/templates/scripts/"

        with contextlib.closing(psycopg2.connect(DB_STRING)) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                for file_name in os.listdir(script_path):
                    try:
                        logger.info(f"rebuilding sales orders script {file_name}: starting execution")
                        with open(f"{script_path}/{file_name}", "r") as f:
                            sql = f.read()
                            cursor.execute(sql)
                            conn.commit()
                        logger.info(f"rebuilding sales orders script {file_name}: completed execution")
                    except Exception:
                        logger.error(
                            f"rebuilding sales orders script {file_name}: failed execution",
                            exc_info=1,
                        )

        logger.info("rebuilding sales orders: completed program")
    except Exception:
        logger.error("rebuilding sales orders: failed program", exc_info=1)


if __name__ == "__main__":
    cli()
