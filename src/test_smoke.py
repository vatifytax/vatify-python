def test_import():
    import vatify
    assert hasattr(vatify, "Vatify")

def test_validate():
    from vatify import Vatify
    import os
    client = Vatify(api_key=os.getenv("VATIFY_API_KEY"))
    try:
        res = client.validate_vat("DE123456789")
        assert not res.valid
    except Exception as e:
        print(f"Error occurred: {e.status_code}, {e.details}")

def test_rates():
    from vatify import Vatify
    import os
    client = Vatify(api_key=os.getenv("VATIFY_API_KEY"))
    res = client.rates("DE")
    assert len(res.reduced_rates) > 0
    assert res.country == "DE"
    assert res.standard_rate != ""


def test_calculate():
    from vatify import Vatify
    from datetime import date
    import os
    client = Vatify(api_key=os.getenv("VATIFY_API_KEY"))
    try:
        res = client.calculate(amount=100, basis="net", rate_type="reduced", supply_date=str(date.today().isoformat()),
                           supplier={"country_code": "DE", "vat_number": "DE811907980"},
                           customer={"country_code": "FR", "vat_number": "FR40303265045"},
                           supply_type="services", b2x="B2B", category_hint="ACCOMMODATION")
    except Exception as e:
        print(f"Error occurred: {e.status_code}, {e.details}")
        return
    assert res.country_code == "FR"

test_import()
test_validate()
test_rates()
test_calculate()