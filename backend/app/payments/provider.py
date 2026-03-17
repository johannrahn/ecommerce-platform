from dataclasses import dataclass
from typing import Protocol


@dataclass
class PaymentResult:
    success: bool
    transaction_id: str
    message: str


class PaymentProvider(Protocol):
    def process_payment(self, amount: float, currency: str) -> PaymentResult: ...


class SimulatedProvider:
    """
    Simulated payment provider for v1.

    Always succeeds unless force_failure is set.
    Deterministic behavior makes it reliable for both demo and testing.
    """

    def __init__(self, force_failure: bool = False):
        self._force_failure = force_failure

    def process_payment(self, amount: float, currency: str = "USD") -> PaymentResult:
        if self._force_failure:
            return PaymentResult(
                success=False,
                transaction_id="sim_failed_000",
                message="Payment declined (simulated failure)",
            )
        return PaymentResult(
            success=True,
            transaction_id=f"sim_{int(amount * 100)}",
            message="Payment accepted (simulated)",
        )


def get_payment_provider() -> SimulatedProvider:
    """FastAPI dependency. Override in tests to inject a failing provider."""
    return SimulatedProvider()
