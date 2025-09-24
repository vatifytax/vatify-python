from __future__ import annotations
import argparse
import os
import sys
from .client import Vatify, VatifyError

def main() -> None:
    parser = argparse.ArgumentParser(prog="vatify", description="Vatify CLI")
    parser.add_argument("--api-key", default=os.getenv("VATIFY_API_KEY"), help="Vatify API key (or set VATIFY_API_KEY)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate a VAT number")
    v.add_argument("vat_number")

    r = sub.add_parser("rates", help="Get VAT rates for a country")
    r.add_argument("country_code")

    c = sub.add_parser("calculate", help="Calculate VAT rate for a country/rate_type/date")
    c.add_argument("country_code")
    c.add_argument("rate_type")
    c.add_argument("supply_date")

    args = parser.parse_args()
    if not args.api_key:
        print("Missing API key. Use --api-key or set VATIFY_API_KEY.", file=sys.stderr)
        sys.exit(2)

    client = Vatify(api_key=args.api_key)
    try:
        if args.cmd == "validate":
            res = client.validate_vat(args.vat_number)
            print(res.model_dump_json(indent=2))
        elif args.cmd == "rates":
            res = client.rates(args.country_code)
            print([r.model_dump() for r in res])
        elif args.cmd == "calculate":
            res = client.calculate(country_code=args.country_code, rate_type=args.rate_type, supply_date=args.supply_date)
            print(res.model_dump_json(indent=2))
    except VatifyError as e:
        print(f"Error: {e} (status={e.status_code})", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()
