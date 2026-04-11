#!/usr/bin/env python3
"""Generate a sample PDF with dummy data for visual QA against the reference form.

Usage:
    cd backend
    python -m scripts.generate_sample_pdf

Output: sample_hlasenie.pdf in the current directory.
"""

import sys
import uuid
from datetime import date, datetime
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models import Child, Guest
from app.services.pdf import generate_pdf


class FakeChild:
    """Minimal child object for PDF generation without a DB session."""

    def __init__(self, name: str, position: int) -> None:
        self.name = name
        self.position = position


class FakeGuest:
    """Minimal guest object for PDF generation without a DB session."""

    def __init__(self) -> None:
        self.stay_from = date(2026, 4, 11)
        self.stay_to = date(2026, 4, 18)
        self.first_name = "John"
        self.last_name = "Smith"
        self.date_of_birth = date(1985, 3, 15)
        self.birth_place = "London, United Kingdom"
        self.nationality = "British"
        self.permanent_address = "42 Baker Street, London NW1 6XE, United Kingdom"
        self.travel_purpose = "Tourism"
        self.passport_number = "GB123456789"
        self.visa_details = ""
        self.accommodation_name = "Penzión Horský Dom"
        self.accommodation_address = "Hlavná 123, 811 01 Bratislava"
        self.children = [
            FakeChild("Emily Smith", 1),
            FakeChild("James Smith", 2),
        ]


def make_sample_guest() -> FakeGuest:  # type: ignore[return]
    """Create a fake guest object with sample data (no DB required)."""
    return FakeGuest()


def main() -> None:
    guest = make_sample_guest()
    buf = generate_pdf(guest)

    output = Path("sample_hlasenie.pdf")
    output.write_bytes(buf.read())
    print(f"Generated: {output.resolve()}")
    print("Compare visually against spec/examples/hlasenie-pobytu-SVK.pdf")


if __name__ == "__main__":
    main()
