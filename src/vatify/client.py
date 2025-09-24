from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
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

class CalculationRequest(BaseModel):
    country_code: str
    rate_type: str  # e.g. "standard" | "reduced"
    supply_date: str  # ISO date "YYYY-MM-DD"

class CalculationResult(BaseModel):
    country_code: str
    rate_type: str
    rate_percent: float
    supply_date: str
    meta: Dict[str, Any] = Field(default_factory=dict)

class Rate(BaseModel):
    country_code: str
    rate_type: str
    rate_percent: float
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None

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
    def calculate(self, *, country_code: str, rate_type: str, supply_date: str) -> CalculationResult:
        c = self._ensure_client()
        payload = CalculationRequest(country_code=country_code, rate_type=rate_type, supply_date=supply_date).model_dump()
        try:
            resp = c.post("/v1/calculate", json=payload)
            if resp.status_code >= 400:
                raise VatifyError("Calculation failed", resp.status_code, resp.text)
            return CalculationResult(**resp.json())
        except httpx.HTTPError as e:
            raise VatifyError(f"Network error: {e}") from e

    # GET /v1/rates/{country_code}
    def rates(self, country_code: str) -> List[Rate]:
        c = self._ensure_client()
        try:
            resp = c.get(f"/v1/rates/{country_code}")
            if resp.status_code >= 400:
                raise VatifyError("Fetching rates failed", resp.status_code, resp.text)
            data = resp.json()
            # Accept either {"rates":[...]} or a raw list
            items = data["rates"] if isinstance(data, dict) and "rates" in data else data
            return [Rate(**r) for r in items]
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

    async def calculate(self, *, country_code: str, rate_type: str, supply_date: str) -> CalculationResult:
        c = self._ensure_client()
        payload = CalculationRequest(country_code=country_code, rate_type=rate_type, supply_date=supply_date).model_dump()
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
