from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional, Dict, Any, List
import httpx
from pydantic import BaseModel, Field

DEFAULT_BASE_URL = "https://api.vatifytax.app"

# ---------- Models ----------
class ValidationResult(BaseModel):
    vat_number: str
    valid: bool
    country_code: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class Supplier(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO-3166-1 alpha-2")
    vat_number: Optional[str] = Field(None, description="Für B2B/VIES-Check")


class CalculationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Eingabebetrag (net oder gross)")
    basis: Literal["net", "gross"] = "net"
    rate_type: Literal["standard", "reduced", "super_reduced", "parking", "zero"] = "standard"
    supply_date: str
    supplier: Supplier
    customer: Supplier
    supply_type: Literal["goods", "services"] = "goods"
    b2x: Literal["B2C", "B2B"] = "B2C"
    category_hint: Optional[str] = Field(None, description="z.B. ebooks, hospitality, food")



class CalculationResult(BaseModel):
    country_code: str
    applied_rate: float
    net: float
    vat: float
    gross: float
    mechanism: Optional[str] = None
    messages: List[str] 
    vat_check_status: str

class Rate(BaseModel):
    rate: float
    label: str

class Rates(BaseModel):
    country: str
    standard_rate: str
    reduced_rates: List[Rate]

# ---------- Errors ----------
class VatifyError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, details: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details

# ---------- Sync Client ----------
@dataclass
class Vatify:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 10.0
    _client: Optional[httpx.Client] = None

    def _ensure_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Authorization": f"Bearer {self.api_key}", "User-Agent": "vatify-python/0.1"},
                follow_redirects=True,
            )
        return self._client

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    # POST /v1/validate-vat  body {"vat_number":"..."}
    def validate_vat(self, vat_number: str) -> ValidationResult:
        c = self._ensure_client()
        try:
            resp = c.post("/v1/validate-vat", json={"vat_number": vat_number})
            if resp.status_code >= 400:
                raise VatifyError("Validation failed", resp.status_code, resp.text)
            data = resp.json()
            # Map permissively in case API adds fields
            return ValidationResult(**data)
        except httpx.HTTPError as e:
            raise VatifyError(f"Network error: {e}") from e

    # POST /v1/calculate  body {"country_code":"...","rate_type":"...","supply_date":"..."}
    def calculate(self, *, amount: float, basis: str, rate_type: str, supply_date: str, supplier: Supplier, customer: Supplier, supply_type: str, b2x: str, category_hint: Optional[str] = None) -> CalculationResult:
        c = self._ensure_client()
        payload = CalculationRequest(amount=amount, basis=basis, rate_type=rate_type, supply_date=supply_date, supplier=supplier, customer=customer, supply_type=supply_type, b2x=b2x, category_hint=category_hint).model_dump()
        try:
            resp = c.post("/v1/calculate", json=payload)
            if resp.status_code >= 400:
                raise VatifyError("Calculation failed", resp.status_code, resp.text)
            return CalculationResult(**resp.json())
        except httpx.HTTPError as e:
            raise VatifyError(f"Network error: {e}") from e

    # GET /v1/rates/{country_code}
    def rates(self, country_code: str) -> Rate:
        c = self._ensure_client()
        try:
            resp = c.get(f"/v1/rates/{country_code}")
            if resp.status_code >= 400:
                raise VatifyError("Fetching rates failed", resp.status_code, resp.text)
            data = resp.json()
            # Accept either {"rates":[...]} or a raw list
            items = data["rates"] if isinstance(data, dict) and "rates" in data else data
            rates = Rates(country=items.get("country", country_code), standard_rate="", reduced_rates=[])
            rates.country = items["country"]
            rates.standard_rate = items["standard_rate"] 
            rates.reduced_rates = [Rate(**r) for r in items["reduced_rates"]]
            return rates
        except httpx.HTTPError as e:
            raise VatifyError(f"Network error: {e}") from e

# ---------- Async Client ----------
@dataclass
class VatifyAsync:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 10.0
    _client: Optional[httpx.AsyncClient] = None

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Authorization": f"Bearer {self.api_key}", "User-Agent": "vatify-python/0.1"},
                follow_redirects=True,
            )
        return self._client

    async def aclose(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def validate_vat(self, vat_number: str) -> ValidationResult:
        c = self._ensure_client()
        try:
            resp = await c.post("/v1/validate-vat", json={"vat_number": vat_number})
            if resp.status_code >= 400:
                raise VatifyError("Validation failed", resp.status_code, await resp.aread())
            return ValidationResult(**resp.json())
        except httpx.HTTPError as e:
            raise VatifyError(f"Network error: {e}") from e

    async def calculate(self, *, amount: float, basis: str, rate_type: str, supply_date: str, supplier: Supplier, customer: Supplier, supply_type: str, b2x: str, category_hint: Optional[str] = None) -> CalculationResult:
        c = self._ensure_client()
        payload = CalculationRequest(amount=amount, basis=basis, rate_type=rate_type, supply_date=supply_date, supplier=supplier, customer=customer, supply_type=supply_type, b2x=b2x, category_hint=category_hint).model_dump()
        try:
            resp = await c.post("/v1/calculate", json=payload)
            if resp.status_code >= 400:
                raise VatifyError("Calculation failed", resp.status_code, await resp.aread())
            return CalculationResult(**resp.json())
        except httpx.HTTPError as e:
            raise VatifyError(f"Network error: {e}") from e

    async def rates(self, country_code: str) -> List[Rate]:
        c = self._ensure_client()
        try:
            resp = await c.get(f"/v1/rates/{country_code}")
            if resp.status_code >= 400:
                raise VatifyError("Fetching rates failed", resp.status_code, await resp.aread())
            data = resp.json()
            items = data["rates"] if isinstance(data, dict) and "rates" in data else data
            return [Rate(**r) for r in items]
        except httpx.HTTPError as e:
            raise VatifyError(f"Network error: {e}") from e
