#!/usr/bin/env python3
"""
End-to-end test of transaction classification.
Runs all transactions through DMN, then LLM fallback for unclassified.
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from classify_transaction import classify_transaction, extract_account_from_budget

# Transaction data from Bill.com API (Nov 1-15, 2025)
TRANSACTIONS = [
    {"uuid": "1", "rawMerchantName": "AMTRAK MOBILE", "merchantCategoryCode": "4112", "amount": 146, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "2", "rawMerchantName": "AMTRAK MOBILE", "merchantCategoryCode": "4112", "amount": 146, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "3", "rawMerchantName": "GULF OIL 91429455", "merchantCategoryCode": "5541", "amount": 59, "budgetName": "Maintenance - Trucks", "userEmail": "arjgoodman87@gmail.com"},
    {"uuid": "4", "rawMerchantName": "Staples Inc VT", "merchantCategoryCode": "5111", "amount": 3682.65, "budgetName": "Wash Cost - Miscellaneous", "userEmail": "ana@washcyclelaundry.com"},
    {"uuid": "5", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 250, "budgetName": "Coin Wash Fees", "userEmail": "martintracey74@gmail.com"},
    {"uuid": "6", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 250, "budgetName": "Coin Wash Fees", "userEmail": "martintracey74@gmail.com"},
    {"uuid": "7", "rawMerchantName": "GOOGLE*CLOUD ZPC8VJ", "merchantCategoryCode": "7399", "amount": 381.55, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "8", "rawMerchantName": "Amazon.com*B833B1GI0", "merchantCategoryCode": "5942", "amount": 50.62, "budgetName": "Chemicals and Detergent", "userEmail": "jessica@washcyclelaundry.com"},
    {"uuid": "9", "rawMerchantName": "CURB SVC - TAXI APP", "merchantCategoryCode": "4121", "amount": 42.16, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "10", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 250, "budgetName": "Coin Wash Fees", "userEmail": "martintracey74@gmail.com"},
    {"uuid": "11", "rawMerchantName": "JETBLUE 2792196311296", "merchantCategoryCode": "3174", "amount": 366.97, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "12", "rawMerchantName": "JETBLUE 2792196313037", "merchantCategoryCode": "3174", "amount": 88.49, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "13", "rawMerchantName": "SUNOCO 0004813209", "merchantCategoryCode": "5541", "amount": 59.99, "budgetName": "Maintenance - Trucks", "userEmail": "arjgoodman87@gmail.com"},
    {"uuid": "14", "rawMerchantName": "TWILIO SENDGRID", "merchantCategoryCode": "5734", "amount": 19.95, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "15", "rawMerchantName": "AMTRAK.COM", "merchantCategoryCode": "4112", "amount": 332, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "16", "rawMerchantName": "AMTRAK.COM", "merchantCategoryCode": "4112", "amount": 274, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "17", "rawMerchantName": "GITHUB, INC.", "merchantCategoryCode": "7372", "amount": 15.12, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "18", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 250, "budgetName": "Coin Wash Fees", "userEmail": "martintracey74@gmail.com"},
    {"uuid": "19", "rawMerchantName": "UBIQUITI INC.", "merchantCategoryCode": "5734", "amount": 690.01, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "20", "rawMerchantName": "Regus Management Group BC", "merchantCategoryCode": "6513", "amount": 1206.83, "budgetName": "5209 - Office Rent", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "21", "rawMerchantName": "AIRBYTE", "merchantCategoryCode": "5734", "amount": 10.6, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "22", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 100, "budgetName": "Coin Wash Fees", "userEmail": "jessica@washcyclelaundry.com"},
    {"uuid": "23", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 150, "budgetName": "Coin Wash Fees", "userEmail": "jessica@washcyclelaundry.com"},
    {"uuid": "24", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 100, "budgetName": "Maintenance - Trucks", "userEmail": "arjgoodman87@gmail.com"},
    {"uuid": "25", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 15, "budgetName": "Coin Wash Fees", "userEmail": "jessica@washcyclelaundry.com"},
    {"uuid": "26", "rawMerchantName": "ROSEWEBSVC* ROSE WEB S", "merchantCategoryCode": "5734", "amount": 43.99, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "27", "rawMerchantName": "ARDUINO CREATE", "merchantCategoryCode": "5065", "amount": 7.41, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "28", "rawMerchantName": "SUNOCO 0004886822", "merchantCategoryCode": "5541", "amount": 50, "budgetName": "Maintenance - Trucks", "userEmail": "arjgoodman87@gmail.com"},
    {"uuid": "29", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 250, "budgetName": "Coin Wash Fees", "userEmail": "martintracey74@gmail.com"},
    {"uuid": "30", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 200, "budgetName": "Coin Wash Fees", "userEmail": "martintracey74@gmail.com"},
    {"uuid": "31", "rawMerchantName": "Twilio TJJTX7FHSLQC42B9", "merchantCategoryCode": "5734", "amount": 18.44, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "32", "rawMerchantName": "PPA ON STREET KIOSKS", "merchantCategoryCode": "7523", "amount": 0.25, "budgetName": "Delivery Cost - Gas Tolls Fines", "userEmail": "arjgoodman87@gmail.com"},
    {"uuid": "33", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 250, "budgetName": "Coin Wash Fees", "userEmail": "martintracey74@gmail.com"},
    {"uuid": "34", "rawMerchantName": "PMUSA 303010 PHILADELP", "merchantCategoryCode": "7523", "amount": 3.95, "budgetName": "Delivery Cost - Gas Tolls Fines", "userEmail": "jessica@washcyclelaundry.com"},
    {"uuid": "35", "rawMerchantName": "PPA ON STREET KIOSKS", "merchantCategoryCode": "7523", "amount": 1, "budgetName": "Delivery Cost - Gas Tolls Fines", "userEmail": "arjgoodman87@gmail.com"},
    {"uuid": "36", "rawMerchantName": "Amazon.com*NK3199H02", "merchantCategoryCode": "5942", "amount": 29.54, "budgetName": "Chemicals and Detergent", "userEmail": "jessica@washcyclelaundry.com"},
    {"uuid": "37", "rawMerchantName": "DELAWARE CORP & TAX WEB", "merchantCategoryCode": "9399", "amount": 300, "budgetName": "5206 - Legal Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "38", "rawMerchantName": "ALDI 60161", "merchantCategoryCode": "5411", "amount": 9.3, "budgetName": "Maintenance - Bikes", "userEmail": "hectfonz1985@gmail.com"},
    {"uuid": "39", "rawMerchantName": "CAUSAL", "merchantCategoryCode": "5734", "amount": 79.79, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "40", "rawMerchantName": "MD.GOV SERVICE FEE", "merchantCategoryCode": "9399", "amount": 1.5, "budgetName": "5206 - Legal Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "41", "rawMerchantName": "MD DEPT ASSMNT/TAX", "merchantCategoryCode": "9399", "amount": 50, "budgetName": "5206 - Legal Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "42", "rawMerchantName": "EXTRA SPACE 1829", "merchantCategoryCode": "4225", "amount": 391.26, "budgetName": "Rent - Production and Storage", "userEmail": "jessica@washcyclelaundry.com"},
    {"uuid": "43", "rawMerchantName": "REVOLUTION LAUNDRY", "merchantCategoryCode": "7211", "amount": 200, "budgetName": "Coin Wash Fees", "userEmail": "martintracey74@gmail.com"},
    {"uuid": "44", "rawMerchantName": "SUNOCO 0374411700", "merchantCategoryCode": "5541", "amount": 50, "budgetName": "Maintenance - Trucks", "userEmail": "arjgoodman87@gmail.com"},
    {"uuid": "45", "rawMerchantName": "DELAWARE CORP & TAX WEB", "merchantCategoryCode": "9399", "amount": 587.5, "budgetName": "5206 - Legal Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "46", "rawMerchantName": "PADDLE.NET* N8N CLOUD1", "merchantCategoryCode": "5817", "amount": 64.8, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "47", "rawMerchantName": "ZOHO* ZOHO-SHIFTS", "merchantCategoryCode": "7379", "amount": 286.03, "budgetName": "5243 - Web Services", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "48", "rawMerchantName": "SOUTH SQUARE MARKET", "merchantCategoryCode": "5411", "amount": 3.49, "budgetName": "Maintenance - Bikes", "userEmail": "hectfonz1985@gmail.com"},
    {"uuid": "49", "rawMerchantName": "CURB SVC - TAXI APP", "merchantCategoryCode": "4121", "amount": 42.16, "budgetName": "5216 - Travel Expenses", "userEmail": "g@washcyclelaundry.com"},
    {"uuid": "50", "rawMerchantName": "MD.GOV SERVICE FEE", "merchantCategoryCode": "9399", "amount": 9, "budgetName": "5206 - Legal Expenses", "userEmail": "g@washcyclelaundry.com"},
]

# User email to team mapping (inferred from typical roles)
USER_TEAMS = {
    "g@washcyclelaundry.com": "Admin",
    "jessica@washcyclelaundry.com": "Production",
    "ana@washcyclelaundry.com": "Production",
    "martintracey74@gmail.com": "Production",
    "arjgoodman87@gmail.com": "Delivery",
    "hectfonz1985@gmail.com": "Delivery",
}

def get_team_for_user(email):
    return USER_TEAMS.get(email, "")

def main():
    config_dir = Path(__file__).parent.parent / "config"
    jdm_path = str(config_dir / "classification_rules.jdm.json")

    results = []
    auto_post = 0
    review = 0
    reject = 0
    discrepancies = 0

    print("=" * 120)
    print(f"{'#':<3} {'Merchant':<30} {'MCC':<5} {'Amount':>10} {'DMN Account':<30} {'Action':<10} {'Discrepancy'}")
    print("=" * 120)

    for txn in TRANSACTIONS:
        team = get_team_for_user(txn["userEmail"])
        employee = {"team": team}

        result = classify_transaction(
            transaction=txn,
            employee=employee,
            billcom_budget=txn["budgetName"],
            jdm_path=jdm_path
        )

        # Track stats
        action = result["action"]
        if action == "AUTO_POST":
            auto_post += 1
        elif action == "REVIEW":
            review += 1
        elif action == "REJECT":
            reject += 1

        if result["has_discrepancy"]:
            discrepancies += 1

        # Format output
        merchant = txn["rawMerchantName"][:28]
        gl_acct = result["gl_account"] or "NONE"
        gl_name = result["gl_account_name"] or ""
        if gl_name:
            gl_display = f"{gl_acct} ({gl_name[:15]})"[:30]
        else:
            gl_display = gl_acct[:30]

        disc_flag = "⚠️ DISCREPANCY" if result["has_discrepancy"] else ""

        print(f"{txn['uuid']:<3} {merchant:<30} {txn['merchantCategoryCode']:<5} ${txn['amount']:>9,.2f} {gl_display:<30} {action:<10} {disc_flag}")

        results.append({
            "id": txn["uuid"],
            "merchant": txn["rawMerchantName"],
            "mcc": txn["merchantCategoryCode"],
            "amount": txn["amount"],
            "billcom_budget": txn["budgetName"],
            "user_team": team,
            "dmn_account": result["gl_account"],
            "dmn_account_name": result["gl_account_name"],
            "action": action,
            "has_discrepancy": result["has_discrepancy"],
            "discrepancy_detail": result.get("discrepancy"),
            "matched_by": result["matched_by"],
            "notes": result["rule_notes"]
        })

    print("=" * 120)
    print(f"\nSUMMARY:")
    print(f"  AUTO_POST: {auto_post} ({auto_post/len(TRANSACTIONS)*100:.1f}%)")
    print(f"  REVIEW:    {review} ({review/len(TRANSACTIONS)*100:.1f}%)")
    print(f"  REJECT:    {reject} ({reject/len(TRANSACTIONS)*100:.1f}%)")
    print(f"  Discrepancies: {discrepancies}")

    # Show REVIEW items that need LLM
    print("\n" + "=" * 120)
    print("ITEMS NEEDING REVIEW (would go to LLM):")
    print("=" * 120)
    for r in results:
        if r["action"] == "REVIEW":
            print(f"  #{r['id']}: {r['merchant'][:35]:<35} MCC:{r['mcc']} ${r['amount']:>8,.2f} → {r['dmn_account'] or 'NONE':<25} Team:{r['user_team']}")
            if r["has_discrepancy"]:
                print(f"       ↳ Bill.com: {r['billcom_budget']}")

    # Show discrepancies
    print("\n" + "=" * 120)
    print("DISCREPANCIES (DMN vs Bill.com):")
    print("=" * 120)
    for r in results:
        if r["has_discrepancy"]:
            print(f"  #{r['id']}: {r['merchant'][:30]}")
            print(f"       DMN says: {r['dmn_account']} ({r['dmn_account_name']})")
            print(f"       Bill.com: {r['billcom_budget']}")
            print()

if __name__ == "__main__":
    main()
