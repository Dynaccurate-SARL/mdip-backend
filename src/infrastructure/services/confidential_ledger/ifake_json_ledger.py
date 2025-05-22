import json
from uuid import UUID, uuid4
from pathlib import Path

from src.infrastructure.services.confidential_ledger.contract import (
    LedgerInterface,
    TransactionInserted,
)
from src.utils.checksum import dict_hash


class FakeJsonLedger(LedgerInterface):
    _instance = None
    _db_file = Path("fake_ledger_db.json")

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FakeJsonLedger, cls).__new__(cls)
        return cls._instance

    def _read_db(self) -> dict:
        if not self._db_file.exists():
            self._db_file.write_text("{}")
        with self._db_file.open("r") as f:
            return json.load(f)

    def _write_db(self, data: dict) -> None:
        with self._db_file.open("w") as f:
            json.dump(data, f, default=str, indent=2)

    def insert_transaction(self, data: dict) -> TransactionInserted:
        transaction_id = uuid4()
        transaction = {
            "transaction_id": str(transaction_id),
            "status": "ready",
            "transaction_data": {"data": data, "hash": dict_hash(data)},
        }
        db = self._read_db()
        db[str(transaction_id)] = transaction
        self._write_db(db)

        return TransactionInserted(**transaction)

    def retrieve_transaction(self, transaction_id: UUID) -> TransactionInserted | None:
        db = self._read_db()
        transaction = db.get(str(transaction_id), None)
        if transaction:
            return TransactionInserted(**transaction)
        return None
