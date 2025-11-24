#!/usr/bin/env python3
"""
Transaction Classifier using GoRules ZEN Engine.

This script classifies Bill.com transactions to ERPNext GL accounts using
a deterministic decision table (JDM format) with discrepancy detection.

Usage:
    python classify_transaction.py --transaction '{"mcc": "5541", ...}' --employee '{"team": "Delivery"}' --billcom_budget "Maintenance - Trucks"

Returns JSON with classification result, confidence, and discrepancy info.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

import zen


# Budget name to account mapping for discrepancy detection
# NOTE: For COGS accounts without numbers, we use the account name as the identifier
# The journal_entry_template.py handles resolving these to full ERPNext account names
BUDGET_TO_ACCOUNT = {
    # Overhead accounts (have account numbers)
    "5206 - Legal Expenses": "5206",
    "5207 - Advertising and Marketing": "5207",
    "5209 - Office Rent": "5209",
    "5210 - Postal Expenses": "5210",
    "5211 - Donations": "5211",
    "5216 - Travel Expenses": "5216",
    "5223 - Bank Fees and Charges": "5223",
    "5229 - Business Taxes & Licenses": "5229",
    "5231 - Computer Equipment": "5231",
    "5232 - Accounting Fees": "5232",
    "5233 - Subcontractor 1099 or UpWork": "5233",
    "5236 - HR Consulting & Hiring": "5236",
    "5237 - Employee Benefits for Admin Staff": "5237",
    "5238 - Insurance": "5238",
    "5239 - Office Expenses": "5239",
    "5240 - Payroll SG&A": "5240",
    "5242 - Telephone & Internet": "5242",
    "5243 - Web Services": "5243",
    "5244 - Consulting": "5244",
    "5245 - Professional business subscriptions": "5245",
    "5246 - Merchant Card Services": "5246",
    "5247 - Payroll Fees": "5247",
    "5251 - Meals and Entertainment": "5251",
    "5252 - Training and Professional Development": "5252",
    "2121 - Owed to WCL Chelsea": "2121",
    "2122 - Owed to WCL DC": "2122",

    # COGS accounts (use account names, no numbers)
    # Delivery Cost
    "Delivery Cost - Gas Tolls Fines": "Gas and Tolls",
    "Gas and Tolls": "Gas and Tolls",
    "Delivery Cost - Vehicle Lease and Mileage": "Vehicle Lease and Mileage",
    "Vehicle Lease and Mileage": "Vehicle Lease and Mileage",
    "Routine Maintenance on Trucks": "Routine Maintenance on Trucks",
    "Bike Maintenance": "Bike Maintenance",
    "Subcontractor for Delivery": "Subcontractor for Delivery",

    # Production / Consumables
    "Chemicals and Detergent": "Chemicals and Detergent",
    "Coin Wash Fees": "Coin Wash Fees",
    "Linen Inventory": "Linen Inventory",
    "Plastic and Bags": "Plastic and Bags",
    "PPE and Safety Supplies": "PPE and Safety Supplies",
    "Consumables for Equipment": "Consumables for Equipment",
    "Break Room and Janitorial Supplies": "Break Room and Janitorial Supplies",
    "Rent - Production and Storage": "Rent - Production and Storage",
    "Outsourcing Washing": "Outsourcing Washing",
    "Intra-Party Subcontractors": "Intra-Party Subcontractors",

    # Maintenance (split from old 5200)
    "Maintenance - Bikes": "Bike Maintenance",
    "Maintenance - Machines": "Plant Equipment - Components for Repairs",
    "Maintenance - Misc": "Building Maintenance",
    "Maintenance - Trucks": "Routine Maintenance on Trucks",  # Often misclassified as gas!
    "Plant Equipment - Components for Repairs": "Plant Equipment - Components for Repairs",
    "Plant Equipment - Third Party Service": "Plant Equipment - Third Party Service",
    "Building Maintenance": "Building Maintenance",
    "Tools - Expensed": "Tools - Expensed",

    # Staff
    "Employee Food and Perks": "Employee Food and Perks",
    "Wash Cost - Employee Food Drinks Perks": "Employee Food and Perks",
    "Employee Uniforms": "Employee Uniforms",
    "Employee Benefits for Production Staff": "Employee Benefits for Production Staff",

    # Mistakes
    "SNAFU": "SNAFU",
    "Customer Credits for Service Errors": "Customer Credits for Service Errors",
    "Tickets and Fines": "Tickets and Fines",
    "Vehicle Damage Claims and Repairs": "Vehicle Damage Claims and Repairs",
    "Errors and Refunds to Customers": "Customer Credits for Service Errors",

    # Legacy mappings (old budget names -> new accounts)
    "Wash Cost - Miscellaneous": "Break Room and Janitorial Supplies",
    "Wash Cost - Plastic and Bags": "Plastic and Bags",
    "Wash Cost - PPE and Uniforms": "PPE and Safety Supplies",
    "Equipment": "Plant Equipment - Components for Repairs",
    "Software Dev": "5243",
}


def extract_account_from_budget(budget_name: str) -> Optional[str]:
    """Extract GL account number from Bill.com budget name."""
    if not budget_name:
        return None

    # Check mapping first
    if budget_name in BUDGET_TO_ACCOUNT:
        return BUDGET_TO_ACCOUNT[budget_name]

    # Try to extract account number from beginning (e.g., "5216 - Travel")
    match = re.match(r'^(\d{4})\s*-', budget_name)
    if match:
        return match.group(1)

    return None


def determine_confidence(result: dict, matched_by: str, has_discrepancy: bool) -> str:
    """Determine confidence level based on match type and discrepancy."""
    action = result.get('action', 'REVIEW')

    if action == 'REJECT':
        return 'REJECT'

    # MCC matches are highest confidence
    if matched_by == 'mcc':
        return 'HIGH'
    elif matched_by == 'merchant':
        return 'MEDIUM' if has_discrepancy else 'HIGH'
    else:
        return 'LOW' if has_discrepancy else 'MEDIUM'


def classify_transaction(
    transaction: dict,
    employee: dict,
    billcom_budget: str,
    jdm_path: str
) -> dict:
    """
    Classify a transaction using the JDM rules engine.

    Args:
        transaction: Dict with keys: mcc, merchant, amount, etc.
        employee: Dict with keys: team, designation, company
        billcom_budget: The budget name assigned in Bill.com
        jdm_path: Path to the JDM rules file

    Returns:
        Dict with classification result and metadata
    """
    # Load JDM rules
    with open(jdm_path, 'r') as f:
        jdm_content = f.read()

    engine = zen.ZenEngine()
    decision = engine.create_decision(jdm_content)

    # Prepare input for decision engine
    input_data = {
        'mcc': transaction.get('merchantCategoryCode') or transaction.get('mcc', ''),
        'merchant': (transaction.get('rawMerchantName') or transaction.get('merchantName') or transaction.get('merchant', '')).upper(),
        'amount': float(transaction.get('amount', 0)),
        'user_team': employee.get('team') or employee.get('department', ''),
        'user_email': transaction.get('userEmail', ''),
        'state_match': transaction.get('state_match', ''),
    }

    # Evaluate rules
    result = decision.evaluate(input_data)
    rule_result = result.get('result', {})

    # Determine what matched
    matched_by = 'none'
    if rule_result.get('gl_account'):
        notes = rule_result.get('notes', '').lower()
        if 'mcc' in notes:
            matched_by = 'mcc'
        elif input_data['merchant']:
            matched_by = 'merchant'
        else:
            matched_by = 'other'

    # Detect discrepancy with Bill.com classification
    billcom_account = extract_account_from_budget(billcom_budget)
    our_account = rule_result.get('gl_account', '').strip('"')
    has_discrepancy = False
    discrepancy_reason = None

    if billcom_account and our_account and billcom_account != our_account:
        has_discrepancy = True
        discrepancy_reason = f"Bill.com budget '{billcom_budget}' suggests account {billcom_account}, but {matched_by.upper()} indicates {our_account}"

    # Determine confidence
    confidence = determine_confidence(rule_result, matched_by, has_discrepancy)

    # Build response
    response = {
        'gl_account': our_account or None,
        'gl_account_name': rule_result.get('gl_account_name', '').strip('"') or None,
        'action': rule_result.get('action', 'REVIEW').strip('"'),
        'confidence': confidence,
        'matched_by': matched_by,
        'rule_notes': rule_result.get('notes', '').strip('"') or None,
        'has_discrepancy': has_discrepancy,
        'discrepancy': {
            'billcom_budget': billcom_budget,
            'billcom_account': billcom_account,
            'our_account': our_account,
            'reason': discrepancy_reason
        } if has_discrepancy else None,
        'input_used': input_data,
        'performance': result.get('performance', '')
    }

    return response


def classify_batch(transactions: list, jdm_path: str) -> list:
    """
    Classify multiple transactions efficiently.

    Args:
        transactions: List of dicts, each with 'transaction', 'employee', 'billcom_budget'
        jdm_path: Path to the JDM rules file

    Returns:
        List of classification results
    """
    # Load JDM rules once
    with open(jdm_path, 'r') as f:
        jdm_content = f.read()

    engine = zen.ZenEngine()
    decision = engine.create_decision(jdm_content)

    results = []
    for item in transactions:
        txn = item.get('transaction', {})
        emp = item.get('employee', {})
        budget = item.get('billcom_budget', '')

        # Prepare input
        input_data = {
            'mcc': txn.get('merchantCategoryCode') or txn.get('mcc', ''),
            'merchant': (txn.get('rawMerchantName') or txn.get('merchantName') or '').upper(),
            'amount': float(txn.get('amount', 0)),
            'user_team': emp.get('team') or emp.get('department', ''),
            'state_match': txn.get('state_match', ''),
        }

        result = decision.evaluate(input_data)
        rule_result = result.get('result', {})

        # Quick classification
        our_account = rule_result.get('gl_account', '').strip('"')
        billcom_account = extract_account_from_budget(budget)
        has_discrepancy = billcom_account and our_account and billcom_account != our_account

        results.append({
            'transaction_id': txn.get('uuid') or txn.get('id'),
            'gl_account': our_account or None,
            'action': rule_result.get('action', 'REVIEW').strip('"'),
            'has_discrepancy': has_discrepancy,
            'billcom_budget': budget,
            'notes': rule_result.get('notes', '').strip('"') or None
        })

    return results


def main():
    parser = argparse.ArgumentParser(description='Classify Bill.com transactions')
    parser.add_argument('--transaction', type=str, help='Transaction JSON')
    parser.add_argument('--employee', type=str, default='{}', help='Employee JSON')
    parser.add_argument('--billcom_budget', type=str, default='', help='Bill.com budget name')
    parser.add_argument('--batch', type=str, help='Batch of transactions JSON (array)')
    parser.add_argument('--jdm', type=str, help='Path to JDM rules file')

    args = parser.parse_args()

    # Determine JDM path
    script_dir = Path(__file__).parent
    jdm_path = args.jdm or str(script_dir / 'classification_rules.jdm.json')

    if args.batch:
        # Batch mode
        transactions = json.loads(args.batch)
        results = classify_batch(transactions, jdm_path)
        print(json.dumps(results, indent=2))
    elif args.transaction:
        # Single transaction mode
        transaction = json.loads(args.transaction)
        employee = json.loads(args.employee)

        result = classify_transaction(
            transaction=transaction,
            employee=employee,
            billcom_budget=args.billcom_budget,
            jdm_path=jdm_path
        )
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
