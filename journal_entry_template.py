#!/usr/bin/env python3
"""
Journal Entry Template for Bill.com to ERPNext Sync.

This module provides a standardized template for creating Journal Entries
from classified Bill.com transactions. It ensures consistent output format
for the LLM when posting to ERPNext.

Usage:
    from journal_entry_template import create_journal_entry

    entry = create_journal_entry(
        company="WCLI",
        posting_date="2025-10-02",
        transaction_id="VHJhbnNhY3Rpb246OWUz...",
        transaction_date="2025-10-01",
        merchant_name="DoorDash",
        user_email="john@example.com",
        amount=52.91,
        expense_account="5216",
        expense_account_name="Travel Expenses"
    )
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import date


# Company configuration
COMPANY_CONFIG = {
    "WCLI": {
        "company_name": "Wash Cycle Laundry Inc.",
        "credit_card_account": "2151 - Divvy Credit Card - WCLI",
        "account_suffix": "WCLI",
    },
    "WCLC": {
        "company_name": "WCL Chelsea LLC",
        "credit_card_account": "2151 - Divvy Credit Card - WCLC",
        "account_suffix": "WCLC",
    },
}

# Account name mapping for accounts that don't follow "{number} - {name} - {suffix}" pattern
# Key: account identifier used in classification, Value: actual ERPNext account name
ACCOUNT_NAME_OVERRIDES = {
    # WCLC accounts without number prefix
    "WCLC": {
        "5150": "Coin Wash Fees - WCLC",  # Default for 5150 in WCLC
        "Chemicals and Detergent": "Chemicals and Detergent - WCLC",
        "Coin Wash Fees": "Coin Wash Fees - WCLC",
        "Delivery Cost - Gas Tolls Fines": "Delivery Cost - Gas Tolls Fines - WCLC",
        "Delivery Cost - Vehicle Lease and Mileage": "Delivery Cost - Vehicle Lease and Mileage - WCLC",
        "Maintenance - Bikes": "Maintenance - Bikes - WCLC",
        "Maintenance - Trucks": "Maintenance - Trucks - WCLC",
        "Rent - Production and Storage": "Rent - Production and Storage - WCLC",
        "Wash Cost - Employee Food Drinks Perks": "Wash Cost - Employee Food Drinks Perks - WCLC",
        "Wash Cost - Miscellaneous": "Wash Cost - Miscellaneous - WCLC",
        "Employee Benefits for Production Staff": "Employee Benefits for Production Staff - WCLC",
    },
    "WCLI": {
        # Add WCLI overrides here if needed
    },
}


@dataclass
class JournalEntryAccount:
    """Single account line in a Journal Entry."""
    account: str
    debit_in_account_currency: float
    credit_in_account_currency: float


@dataclass
class JournalEntry:
    """
    ERPNext Journal Entry structure for Bill.com credit card transactions.

    This template ensures consistent format when creating journal entries
    from classified Bill.com transactions.
    """
    # Required header fields
    doctype: str = "Journal Entry"
    docstatus: int = 0       # 0=Draft, 1=Submitted, 2=Cancelled
    voucher_type: str = "Journal Entry"
    company: str = ""
    posting_date: str = ""

    # Transaction reference fields
    cheque_no: str = ""      # Bill.com base64 transaction ID
    cheque_date: str = ""    # Transaction authorization date
    user_remark: str = ""    # "Merchant: {name} | User: {email}"

    # Account lines
    accounts: list = None

    def __post_init__(self):
        if self.accounts is None:
            self.accounts = []

    def to_dict(self) -> dict:
        """Convert to dictionary for Frappe API."""
        return {
            "doctype": self.doctype,
            "docstatus": self.docstatus,
            "voucher_type": self.voucher_type,
            "company": self.company,
            "posting_date": self.posting_date,
            "cheque_no": self.cheque_no,
            "cheque_date": self.cheque_date,
            "user_remark": self.user_remark,
            "accounts": [asdict(acc) for acc in self.accounts]
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


def resolve_expense_account(company: str, account_number: str, account_name: str) -> str:
    """
    Resolve the full ERPNext account name for an expense account.

    Some accounts follow "{number} - {name} - {suffix}" pattern, others don't.
    This function handles both cases using the ACCOUNT_NAME_OVERRIDES mapping.

    Args:
        company: Company code ("WCLI" or "WCLC")
        account_number: GL account number (e.g., "5216")
        account_name: GL account name (e.g., "Travel Expenses")

    Returns:
        Full ERPNext account name
    """
    suffix = COMPANY_CONFIG[company]["account_suffix"]
    overrides = ACCOUNT_NAME_OVERRIDES.get(company, {})

    # Check if account number has an override
    if account_number in overrides:
        return overrides[account_number]

    # Check if account name has an override
    if account_name in overrides:
        return overrides[account_name]

    # Default: construct standard format
    return f"{account_number} - {account_name} - {suffix}"


def create_journal_entry(
    company: str,
    posting_date: str,
    transaction_id: str,
    transaction_date: str,
    merchant_name: str,
    user_email: Optional[str],
    amount: float,
    expense_account: str,
    expense_account_name: str,
    is_credit: bool = False
) -> dict:
    """
    Create a standardized Journal Entry from a classified Bill.com transaction.

    Args:
        company: Company code ("WCLI" or "WCLC")
        posting_date: Date to post the entry (YYYY-MM-DD), from occurredTime
        transaction_id: Bill.com base64 transaction ID
        transaction_date: Transaction authorization date (YYYY-MM-DD)
        merchant_name: Merchant name from Bill.com
        user_email: Email of user who made the transaction (or None)
        amount: Transaction amount (positive number)
        expense_account: GL account number (e.g., "5216")
        expense_account_name: GL account name (e.g., "Travel Expenses")
        is_credit: True if this is a refund/credit (reverses debit/credit)

    Returns:
        Dictionary ready for Frappe create_document API

    Example:
        >>> entry = create_journal_entry(
        ...     company="WCLI",
        ...     posting_date="2025-10-02",
        ...     transaction_id="VHJhbnNhY3Rpb246OWUz...",
        ...     transaction_date="2025-10-01",
        ...     merchant_name="DoorDash",
        ...     user_email="john@example.com",
        ...     amount=52.91,
        ...     expense_account="5216",
        ...     expense_account_name="Travel Expenses"
        ... )
    """
    if company not in COMPANY_CONFIG:
        raise ValueError(f"Unknown company: {company}. Must be one of: {list(COMPANY_CONFIG.keys())}")

    config = COMPANY_CONFIG[company]

    # Resolve the full expense account name (handles non-standard naming)
    full_expense_account = resolve_expense_account(company, expense_account, expense_account_name)

    # Format user_remark
    user_display = user_email if user_email else "None"
    user_remark = f"Merchant: {merchant_name} | User: {user_display}"

    # Determine debit/credit based on whether it's a refund
    if is_credit:
        # Refund: Debit the credit card (reduce liability), Credit the expense (reduce expense)
        cc_debit = amount
        cc_credit = 0.0
        exp_debit = 0.0
        exp_credit = amount
    else:
        # Normal expense: Credit the credit card (increase liability), Debit the expense
        cc_debit = 0.0
        cc_credit = amount
        exp_debit = amount
        exp_credit = 0.0

    # Build title: "Merchant Auth YYYY-MM-DD"
    title = f"{merchant_name} Auth {transaction_date}"

    # Build the entry
    entry = {
        "doctype": "Journal Entry",
        "docstatus": 0,  # Draft - requires manual submission in ERPNext
        "title": title,
        "voucher_type": "Journal Entry",
        "company": config["company_name"],
        "posting_date": posting_date,
        "cheque_no": transaction_id,
        "cheque_date": transaction_date,
        "user_remark": user_remark,
        "accounts": [
            {
                "account": config["credit_card_account"],
                "debit_in_account_currency": cc_debit,
                "credit_in_account_currency": cc_credit,
            },
            {
                "account": full_expense_account,
                "debit_in_account_currency": exp_debit,
                "credit_in_account_currency": exp_credit,
            }
        ]
    }

    return entry


def create_journal_entry_from_classification(
    transaction: dict,
    classification: dict,
    company: str
) -> dict:
    """
    Create a Journal Entry from a Bill.com transaction and its classification result.

    Args:
        transaction: Bill.com transaction dict (from list_transactions_enriched)
        classification: Classification result dict (from classify_transaction.py)
        company: Company code ("WCLI" or "WCLC")

    Returns:
        Dictionary ready for Frappe create_document API
    """
    # Extract posting date from occurredTime
    occurred_time = transaction.get("occurredTime", "")
    posting_date = occurred_time[:10] if occurred_time else ""

    # Extract transaction date from authorizedTime
    authorized_time = transaction.get("authorizedTime", "")
    transaction_date = authorized_time[:10] if authorized_time else posting_date

    return create_journal_entry(
        company=company,
        posting_date=posting_date,
        transaction_id=transaction.get("id", ""),
        transaction_date=transaction_date,
        merchant_name=transaction.get("merchantName") or transaction.get("rawMerchantName", "Unknown"),
        user_email=transaction.get("userEmail"),
        amount=float(transaction.get("amount", 0)),
        expense_account=classification.get("gl_account", ""),
        expense_account_name=classification.get("gl_account_name", ""),
        is_credit=transaction.get("isCredit", False)
    )


# Template schema for reference (used by LLM for consistent output)
JOURNAL_ENTRY_SCHEMA = {
    "doctype": "Journal Entry",
    "docstatus": 0,  # 0=Draft, 1=Submitted, 2=Cancelled
    "title": "<MERCHANT_NAME> Auth <AUTH_DATE>",  # e.g., "DoorDash Auth 2025-10-01"
    "voucher_type": "Journal Entry",
    "company": "<COMPANY_NAME>",
    "posting_date": "<YYYY-MM-DD>",  # Settlement date (occurredTime)
    "cheque_no": "<BILL_COM_TRANSACTION_ID>",
    "cheque_date": "<YYYY-MM-DD>",  # Authorization date (authorizedTime)
    "user_remark": "Merchant: <MERCHANT_NAME> | User: <USER_EMAIL>",
    "accounts": [
        {
            "account": "<CREDIT_CARD_LIABILITY_ACCOUNT>",
            "debit_in_account_currency": 0,
            "credit_in_account_currency": "<AMOUNT>"
        },
        {
            "account": "<EXPENSE_ACCOUNT>",
            "debit_in_account_currency": "<AMOUNT>",
            "credit_in_account_currency": 0
        }
    ]
}


# Duplicate detection query template
# Use this with Frappe MCP list_documents to check for existing entries
DUPLICATE_CHECK_QUERY = {
    "doctype": "Journal Entry",
    "filters": "cheque_no:{transaction_id}",
    "fields": "name,posting_date,total_debit,docstatus",
    "limit": "1"
}


def get_duplicate_check_instructions(transaction_id: str) -> str:
    """
    Generate instructions for checking if a transaction already exists in ERPNext.

    Args:
        transaction_id: Bill.com base64 transaction ID

    Returns:
        Instructions string for the LLM to execute duplicate check
    """
    return f"""
DUPLICATE CHECK REQUIRED before creating Journal Entry:

Use Frappe MCP list_documents:
    doctype: "Journal Entry"
    filters: "cheque_no:{transaction_id}"
    fields: "name,posting_date,total_debit,docstatus"
    limit: "1"

If results are found:
- SKIP this transaction (already exists)
- Note the existing entry name for reference

If no results:
- Proceed with creating the Journal Entry
"""


if __name__ == "__main__":
    # Example usage
    example_entry = create_journal_entry(
        company="WCLI",
        posting_date="2025-10-02",
        transaction_id="VHJhbnNhY3Rpb246OWUzY2UxMTEtYzU3MS00ZTZhLTg5YjQtMmYxZWU1MGNkZmFl",
        transaction_date="2025-10-01",
        merchant_name="DoorDash",
        user_email="john@example.com",
        amount=52.91,
        expense_account="5216",
        expense_account_name="Travel Expenses"
    )

    print("Example Journal Entry:")
    print(json.dumps(example_entry, indent=2))

    # Example refund
    refund_entry = create_journal_entry(
        company="WCLI",
        posting_date="2025-10-05",
        transaction_id="VHJhbnNhY3Rpb246YWJjMTIz",
        transaction_date="2025-10-04",
        merchant_name="Amazon",
        user_email="jane@example.com",
        amount=25.00,
        expense_account="5239",
        expense_account_name="Office Expenses",
        is_credit=True
    )

    print("\nExample Refund Entry:")
    print(json.dumps(refund_entry, indent=2))
