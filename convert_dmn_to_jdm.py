#!/usr/bin/env python3
"""
Convert DMN CSV rules to GoRules JDM (JSON Decision Model) format.

This script reads dmn_rules.csv and generates a JDM-compatible JSON file
that can be executed by zen-engine for consistent transaction classification.
"""

import csv
import json
import re
from pathlib import Path


def wildcard_to_zen_expression(pattern: str, field: str = "$") -> str:
    """Convert wildcard pattern like *USPS* to ZEN expression."""
    if not pattern:
        return ""

    # Remove leading/trailing wildcards and convert to contains check
    pattern_clean = pattern.strip("*")

    if pattern.startswith("*") and pattern.endswith("*"):
        # *pattern* -> contains
        return f'contains(upper({field}), "{pattern_clean.upper()}")'
    elif pattern.startswith("*"):
        # *pattern -> ends with
        return f'endsWith(upper({field}), "{pattern_clean.upper()}")'
    elif pattern.endswith("*"):
        # pattern* -> starts with
        return f'startsWith(upper({field}), "{pattern_clean.upper()}")'
    else:
        # exact match
        return f'upper({field}) == "{pattern_clean.upper()}"'


def amount_to_zen_expression(min_val: str, max_val: str, field: str = "amount") -> str:
    """Convert amount range to ZEN expression."""
    conditions = []

    if min_val:
        conditions.append(f'{field} >= {float(min_val)}')
    if max_val:
        conditions.append(f'{field} <= {float(max_val)}')

    if len(conditions) == 2:
        return f'({conditions[0]}) and ({conditions[1]})'
    elif len(conditions) == 1:
        return conditions[0]
    return ""


def convert_dmn_to_jdm(csv_path: str, output_path: str) -> dict:
    """Convert DMN CSV to JDM JSON format."""

    rules = []
    rule_id = 0

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip comment lines
            if row.get('merchant_pattern', '').startswith('#'):
                continue

            # Skip empty rows
            if not any(row.values()):
                continue

            # Skip if no gl_account (header rows, etc)
            if not row.get('gl_account'):
                continue

            rule_id += 1

            rule = {
                "_id": f"rule-{rule_id}",
            }

            # Input conditions (handle None values)
            # MCC code (exact match)
            mcc = (row.get('merchant_category') or '').strip()
            if mcc:
                rule['mcc'] = f'"{mcc}"'
            else:
                rule['mcc'] = ''

            # Merchant pattern (wildcard match)
            merchant_pattern = (row.get('merchant_pattern') or '').strip()
            if merchant_pattern:
                rule['merchant_expr'] = wildcard_to_zen_expression(merchant_pattern, 'merchant')
            else:
                rule['merchant_expr'] = ''

            # Amount range
            amount_min = (row.get('amount_min') or '').strip()
            amount_max = (row.get('amount_max') or '').strip()
            if amount_min or amount_max:
                rule['amount_expr'] = amount_to_zen_expression(amount_min, amount_max)
            else:
                rule['amount_expr'] = ''

            # User team
            user_team = (row.get('user_team') or '').strip()
            if user_team:
                rule['user_team'] = f'"{user_team}"'
            else:
                rule['user_team'] = ''

            # State match
            state_match = (row.get('state_match') or '').strip()
            if state_match:
                rule['state_match'] = f'"{state_match}"'
            else:
                rule['state_match'] = ''

            # Outputs (handle None values)
            gl_account = row.get("gl_account") or ""
            gl_account_name = row.get("gl_account_name") or ""
            action = row.get("action") or "REVIEW"
            notes = row.get("notes") or ""

            rule['gl_account'] = f'"{gl_account.strip()}"'
            rule['gl_account_name'] = f'"{gl_account_name.strip()}"'
            rule['action'] = f'"{action.strip()}"'
            rule['notes'] = f'"{notes.strip()}"'

            rules.append(rule)

    # Build JDM structure
    jdm = {
        "contentType": "application/vnd.gorules.decision",
        "nodes": [
            {
                "id": "input",
                "type": "inputNode",
                "name": "Request",
                "position": {"x": 0, "y": 0}
            },
            {
                "id": "output",
                "type": "outputNode",
                "name": "Response",
                "position": {"x": 600, "y": 0}
            },
            {
                "id": "classify-transaction",
                "type": "decisionTableNode",
                "name": "Classify Transaction",
                "position": {"x": 300, "y": 0},
                "content": {
                    "hitPolicy": "first",
                    "inputs": [
                        {"id": "mcc", "name": "MCC Code", "field": "mcc"},
                        {"id": "merchant_expr", "name": "Merchant Match", "field": ""},  # Expression mode
                        {"id": "amount_expr", "name": "Amount Range", "field": ""},  # Expression mode
                        {"id": "user_team", "name": "User Team", "field": "user_team"},
                        {"id": "state_match", "name": "State Match", "field": "state_match"}
                    ],
                    "outputs": [
                        {"id": "gl_account", "name": "GL Account", "field": "gl_account"},
                        {"id": "gl_account_name", "name": "Account Name", "field": "gl_account_name"},
                        {"id": "action", "name": "Action", "field": "action"},
                        {"id": "notes", "name": "Notes", "field": "notes"}
                    ],
                    "rules": rules
                }
            }
        ],
        "edges": [
            {"id": "edge-1", "sourceId": "input", "targetId": "classify-transaction"},
            {"id": "edge-2", "sourceId": "classify-transaction", "targetId": "output"}
        ]
    }

    # Write output
    with open(output_path, 'w') as f:
        json.dump(jdm, f, indent=2)

    print(f"Converted {len(rules)} rules to JDM format")
    print(f"Output written to: {output_path}")

    return jdm


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    csv_path = script_dir / "dmn_rules.csv"
    output_path = script_dir / "classification_rules.jdm.json"

    convert_dmn_to_jdm(str(csv_path), str(output_path))
