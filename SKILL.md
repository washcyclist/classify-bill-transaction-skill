# Bill.com Spend & Expense to ERPNext Sync Skill

This skill syncs, classifies, and reconciles credit card transactions from Bill.com Spend & Expense to ERPNext using a combination of deterministic DMN rules and LLM-based classification.

## Overview

The skill performs the following workflow:
1. **Company Selection**: Prompt user to select which company to process
2. **Date Range**: Prompt for date range (defaults to last week)
3. **Fetch Transactions**: Get cleared transactions from Bill.com via MCP
4. **Enrich Data**: Look up employee information from ERPNext
5. **Classify**: Apply DMN rules first, then LLM for non-matches
6. **Present for Review**: Show all transactions grouped by confidence level
7. **Create Journal Entries**: After user confirmation, post to ERPNext
8. **Reconcile**: Verify Bill.com transaction sum matches ERPNext GL account

## Company Configuration

There are two active entities, each with separate Bill.com credentials and Chart of Accounts:

| Company | Bill.com Company Param | Credit Card GL Account | Employee Home Base |
|---------|----------------------|----------------------|-------------------|
| Wash Cycle Laundry Inc. | "Wash Cycle Laundry Inc." | 2151 - Divvy Credit Card - WCLI | Philadelphia, PA area |
| WCL Chelsea LLC | "WCL Chelsea LLC" | 2151 - Divvy Credit Card - WCLC | Lynn, MA area |

## Workflow Steps

### Step 1: Company Selection

Ask the user which company to process:
- Wash Cycle Laundry Inc. (WCLI)
- WCL Chelsea LLC (WCLC)

Store the selection for use throughout the workflow.

### Step 2: Date Range Selection

Ask the user for a date range, with the default being last week (Monday-Sunday of the previous week).

Example:
- "What date range would you like to process? (Default: last week, [start_date] to [end_date])"

Accept dates in YYYY-MM-DD format.

### Step 3: Fetch Transactions from Bill.com

Use the Bill.com MCP server's `list_transactions_enriched` tool to fetch cleared transactions:

```
list_transactions_enriched(
    company="[company name from Step 1]",
    start_date="YYYY-MM-DD",
    end_date="YYYY-MM-DD",
    transaction_type="CLEAR",
    page=1,
    page_size=100
)
```

**CRITICAL**: Check the `hasMorePages` field in the response. If `true`, you MUST continue fetching with incremented page numbers until all transactions are retrieved.

The enriched response includes:
- `id`: Base64 encoded transaction ID
- `uuid`: Transaction UUID (e.g., "txr_kkgu2h2p5h6v9a4o6gbn8tmc2g")
- `userEmail`: User who made the transaction
- `merchantName`: Cleaned merchant name
- `rawMerchantName`: Original merchant name (uppercase)
- `budgetName`: Human-readable budget name
- `amount`: Transaction amount in dollars (e.g., 200 = $200.00)
- `occurredTime`: When transaction cleared (use for posting date)
- `authorizedTime`: When transaction was authorized
- `merchantLocation`: Location object with structure:
  ```json
  {
    "city": "PHILADELPHIA",
    "state": "PA",
    "postalCode": "19139",
    "country": "US"
  }
  ```
- `merchantCategoryCode`: MCC code (e.g., "7211" for dry cleaners/laundry)
- `isReconciled`: Whether already reconciled (boolean)
- `isLocked`: Whether transaction is locked (boolean)
- `isCredit`: Whether this is a credit/refund (boolean)
- `cardPresent`: Whether physical card was used (boolean)
- `receiptStatus`: Receipt status (e.g., "ATTACHED", "MISSING")

### Step 4: Enrich with Employee Data

For each transaction, look up the employee in ERPNext using the `userEmail`:

Use Frappe MCP `list_documents` tool:
```
list_documents(
    doctype="Employee",
    filters="user_id:[email]",
    fields="name,employee_name,company,department,designation"
)
```

Extract:
- Employee's **company** (for multi-entity check)
- Employee's **city** (infer from company: WCLI = Philadelphia area, WCLC = Lynn, MA area)
- Employee's **team/department** for classification rules
- Employee's **designation** for classification rules

**IMPORTANT**: If the employee's company doesn't match the Bill.com company selected in Step 1, flag this as an error and exclude from processing.

### Step 5: Classification

**CRITICAL PRINCIPLE: Do NOT trust Bill.com budget classifications.**

Users frequently misclassify transactions in Bill.com. Our classification must be based on objective signals in this priority order:

1. **MCC Code** (Highest priority) - Industry-standard merchant category codes are the most reliable signal
2. **Merchant Name Pattern** - Recognized merchant names provide strong classification hints
3. **Employee Context** - Team/department helps distinguish travel vs delivery vs overhead
4. **Location Context** - LOCAL vs OUT_OF_STATE affects account selection
5. **Bill.com Budget** (Lowest priority) - Only use as a hint; always verify against other signals

#### 5A: Classification Using Python Script (Recommended)

Use the `classify_transaction.py` script with the GoRules ZEN engine for **consistent, deterministic classification**. This ensures the same transaction always gets the same classification.

**Setup** (one-time):
```bash
cd /path/to/skill
python3 -m venv .venv
.venv/bin/pip install zen-engine
```

**Single Transaction Classification**:
```bash
.venv/bin/python3 classify_transaction.py \
  --transaction '{"merchantCategoryCode": "5541", "rawMerchantName": "SUNOCO", "amount": 60, "state_match": "LOCAL"}' \
  --employee '{"team": "Delivery"}' \
  --billcom_budget "Maintenance - Trucks"
```

**Response**:
```json
{
  "gl_account": "5110",
  "gl_account_name": "Gas Tolls Fines",
  "action": "AUTO_POST",
  "confidence": "HIGH",
  "matched_by": "mcc",
  "rule_notes": "Gas for delivery vehicles (MCC: service station)",
  "has_discrepancy": true,
  "discrepancy": {
    "billcom_budget": "Maintenance - Trucks",
    "billcom_account": "5200",
    "our_account": "5110",
    "reason": "Bill.com budget 'Maintenance - Trucks' suggests account 5200, but MCC indicates 5110"
  }
}
```

**Batch Classification** (more efficient for multiple transactions):
```bash
.venv/bin/python3 classify_transaction.py --batch '[
  {"transaction": {...}, "employee": {...}, "billcom_budget": "..."},
  {"transaction": {...}, "employee": {...}, "billcom_budget": "..."}
]'
```

#### 5B: Determine Travel Status

Before calling the classifier, determine if the transaction is LOCAL or OUT_OF_STATE:

1. Extract the state from `merchantLocation.state` (e.g., "PA", "MA")
2. Compare to employee's home state:
   - Philadelphia area (WCLI) → PA is LOCAL
   - Lynn, MA area (WCLC) → MA is LOCAL
3. Add `state_match: "LOCAL"` or `state_match: "OUT_OF_STATE"` to the transaction object

**Note**: The `merchantLocation` object contains `city`, `state`, `postalCode`, and `country` fields.

#### 5C: Classification Rules (JDM Format)

The rules are stored in `classification_rules.jdm.json` (GoRules JDM format) and executed by the ZEN engine.

**Rule Priority** (first match wins):
1. **MCC-based rules** - Highest priority, most reliable
2. **Merchant pattern rules** - Secondary, based on merchant name
3. **Context rules** - Consider employee team, location, amount

**To modify rules**:
1. Edit `dmn_rules.csv` (human-readable format)
2. Run `python3 convert_dmn_to_jdm.py` to regenerate the JDM file
3. Test with sample transactions

**DMN CSV columns**:
- `merchant_pattern`: Wildcard pattern (e.g., "*USPS*")
- `merchant_category`: MCC code (PRIORITIZE these)
- `amount_min`, `amount_max`: Amount range
- `user_team`: Employee team/department
- `state_match`: LOCAL or OUT_OF_STATE
- `gl_account`: Target GL account code
- `action`: AUTO_POST, REVIEW, or REJECT
- `notes`: Explanation

#### 5D: LLM Classification for Non-Matches

For transactions that don't match any DMN rule, use LLM classification:

1. Load the chart of accounts and classification philosophy from `chart_of_accounts.json` (located in the same directory as this skill file). This includes:
   - All account definitions with descriptions
   - MCC code mappings
   - Classification philosophy (consistency, materiality, COGS vs overhead)
2. Read the ERPNext Chart of Accounts using Frappe MCP:
   ```
   list_documents(
       doctype="Account",
       filters="company:[company name],is_group:0",
       fields="name,account_name,account_type,account_number"
   )
   ```
3. Construct a classification prompt with:
   - Transaction details (merchant, amount, user, location)
   - Employee details (team, role, home location)
   - Travel status (LOCAL vs OUT_OF_STATE)
   - Narrative rules
   - Account list with descriptions

4. Ask Claude to:
   - Classify to the most appropriate GL account
   - Provide 2-3 alternative accounts with reasoning
   - Assign confidence level: HIGH (>90%), MEDIUM (70-90%), LOW (<70%)

5. For HIGH confidence (>90%), mark as AUTO_POST
6. For MEDIUM/LOW confidence, mark as REVIEW

#### 5E: Discrepancy Detection

After classifying each transaction, compare our classification to the Bill.com budget:

1. **Extract Bill.com Account Suggestion**:
   - If budget name contains an account number (e.g., "5216 - Travel Expenses"), extract it
   - If budget name is descriptive (e.g., "Maintenance - Trucks"), map to likely account

2. **Detect Discrepancies**:
   - Compare our classified GL account to Bill.com's suggested account
   - If they differ, flag as a discrepancy with:
     - `has_discrepancy: true`
     - `billcom_account: [their suggestion]`
     - `our_account: [our classification]`
     - `discrepancy_reason: [explanation]`

3. **Common Discrepancy Patterns** (auto-detect and explain):
   | Bill.com Says | MCC/Merchant Indicates | Correct Account | Reason |
   |---------------|----------------------|-----------------|--------|
   | Maintenance - Trucks | MCC 5541 (gas station) | 5110 Gas Tolls Fines | MCC 5541 = service stations |
   | Maintenance - Trucks | MCC 7523 (parking) | 5110 Gas Tolls Fines | MCC 7523 = parking lots |
   | Travel Expenses | MCC 5734/7372 (software) | 5900 Web Services | Software subscriptions |
   | Travel Expenses | MCC 9402 (postal) | 5660 Shipping | USPS/postal services |
   | Travel Expenses | MCC 5968 (subscription) | 5245 Prof Subscriptions | Recurring subscriptions |
   | Any | MCC 7211 (laundry) | 5150 Coin Wash Fees | Laundromat services |

4. **Confidence Adjustment for Discrepancies**:
   - **MCC-based classification with discrepancy**: Keep HIGH confidence (MCC is authoritative)
   - **Merchant pattern with discrepancy**: Reduce to MEDIUM confidence
   - **LLM classification with discrepancy**: Reduce to LOW confidence, mark for REVIEW

5. **Track Discrepancy Statistics**:
   - Count total discrepancies found
   - Track by user (identifies employees who need training)
   - Track by category (identifies systematic misclassification patterns)

#### 5F: Special Cases

**Mileage Reimbursements**:
- If merchant contains "mileage" or user classification is "mileage"
- Calculate: miles × $0.70 per mile
- Post to GL account 5800 (Travel)
- Flag for REVIEW to verify mileage amount

**Large Equipment Purchases**:
- If amount > $5,000 and merchant is hardware/equipment store
- Flag as REJECT with note: "Potential asset - requires manual review"

**Credits/Refunds**:
- If `isCredit: true`, reverse the journal entry (debit liability, credit expense)
- Try to match to original transaction for consistent GL account

### Step 6: Present for Review

Group transactions by confidence/action level and present in chat:

#### ✅ AUTO_POST - High Confidence (DMN matches and LLM >90%)
```
Total: $X,XXX.XX across N transactions

1. [Date] - [Merchant] - $XXX.XX
   User: [Email] | MCC: [Code]
   Classification: [Account Number] - [Account Name]
   Rule: [DMN rule notes or "LLM classification"]
   ⚡ OVERRIDE: Bill.com said "[Budget Name]" - corrected based on MCC [if discrepancy]

2. [...]
```

#### ⚠️ REVIEW - Medium/Low Confidence
```
Total: $X,XXX.XX across N transactions

1. [Date] - [Merchant] - $XXX.XX
   User: [Email] | MCC: [Code] | Bill.com: [Budget Name]

   Suggested: [Account Number] - [Account Name]
   Confidence: [XX%]

   ⚡ DISCREPANCY: Bill.com classified as "[Budget]" but [reason for our classification]

   Alternatives:
   - [Account Number] - [Account Name]: [Reason]
   - [Account Number] - [Account Name]: [Reason]

   Please confirm or specify correct account.

2. [...]
```

#### 🚩 REJECTED - Requires Manual Handling
```
Total: $X,XXX.XX across N transactions

1. [Date] - [Merchant] - $XXX.XX
   User: [Email] | Budget: [Budget Name]

   Reason: [Why rejected - e.g., "Potential asset", "Multi-entity mismatch"]

   This transaction should be handled manually.

2. [...]
```

**Summary Statistics**:
```
📊 Classification Summary
─────────────────────────────────────────
Total transactions: N
Total amount: $XX,XXX.XX

✅ AUTO_POST: N transactions ($XX,XXX.XX)
⚠️ REVIEW:    N transactions ($XX,XXX.XX)
🚩 REJECTED:  N transactions ($XX,XXX.XX)

⚡ Discrepancies Found: N transactions
   - Corrected automatically: N (high confidence MCC matches)
   - Flagged for review: N (lower confidence)

📈 Discrepancies by User:
   - [user@email.com]: N transactions
   - [user2@email.com]: N transactions

📉 Common Misclassification Patterns:
   - Gas stations → "Maintenance": N occurrences
   - Software → "Travel": N occurrences
```

### Step 7: Get User Confirmation

For REVIEW transactions, iterate through each and ask the user to:
- Confirm the suggested account, OR
- Specify a different account number

Update each transaction with the user's decision.

Ask: "Ready to create journal entries in ERPNext for AUTO_POST and confirmed REVIEW items? (REJECTED items will be skipped)"

### Step 8: Create Journal Entries

For each approved transaction (AUTO_POST + confirmed REVIEW items), create a journal entry in ERPNext.

#### 8A: Duplicate Detection (CRITICAL)

**Before creating any Journal Entry**, check if the transaction already exists:

```
list_documents(
    doctype="Journal Entry",
    filters="cheque_no:{transaction_id}",
    fields="name,posting_date,total_debit,docstatus",
    limit="1"
)
```

Where `{transaction_id}` is the Bill.com base64 transaction ID (the `id` field from Bill.com).

- **If results found**: SKIP this transaction - it already exists in ERPNext
- **If no results**: Proceed with creating the Journal Entry

**Why this matters**: The `cheque_no` field stores the unique Bill.com transaction ID. Without this check, the same transaction can be entered multiple times (this has happened before with 12+ duplicates).

#### 8B: Using the Template (Recommended)

Use `journal_entry_template.py` to generate consistent Journal Entry format:

```python
from journal_entry_template import create_journal_entry, create_journal_entry_from_classification

# From classified transaction
entry = create_journal_entry_from_classification(
    transaction=billcom_transaction,
    classification=classification_result,
    company="WCLI"
)

# Or manually
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
```

#### 8C: Frappe API Call

Use Frappe MCP `create_document` tool with the generated entry:

```
create_document(
    doctype="Journal Entry",
    values={
        "voucher_type": "Journal Entry",
        "company": "Wash Cycle Laundry Inc.",
        "posting_date": "2025-10-02",
        "cheque_no": "[Bill.com base64 transaction ID]",
        "cheque_date": "2025-10-01",
        "user_remark": "Merchant: DoorDash | User: john@example.com",
        "accounts": [
            {
                "account": "2151 - Divvy Credit Card - WCLI",
                "debit_in_account_currency": 0,
                "credit_in_account_currency": 52.91
            },
            {
                "account": "5216 - Travel Expenses - WCLI",
                "debit_in_account_currency": 52.91,
                "credit_in_account_currency": 0
            }
        ]
    }
)
```

**Critical Fields**:
- `voucher_type`: Always `"Journal Entry"` for credit card expenses
- `posting_date`: Use `occurredTime` date from Bill.com (when transaction cleared)
- `cheque_no`: Bill.com base64 transaction ID (for duplicate detection)
- `cheque_date`: Transaction authorization date
- `user_remark`: Format as `"Merchant: {name} | User: {email}"`
- `company`: Must match the company selected in Step 1

**Account Selection**:
- **Row 1 - Credit Card Liability (CREDIT)**:
  - WCLI: `"2151 - Divvy Credit Card - WCLI"`
  - WCLC: `"2151 - Divvy Credit Card - WCLC"`
- **Row 2 - Expense Account (DEBIT)**:
  - Format: `"{account_number} - {account_name} - {suffix}"`
  - Example: `"5216 - Travel Expenses - WCLI"`

**Refunds/Credits**:
For refund transactions (`isCredit: true`), the template automatically reverses:
- Debit the credit card (reduces liability)
- Credit the expense account (reduces expense)

Track successes and failures. Report any errors clearly.

### Step 9: Reconciliation Check

After creating journal entries, verify the totals match:

1. **Bill.com Side**: Sum the amounts of all processed transactions
2. **ERPNext Side**: Query journal entries for the date range:
   ```
   list_documents(
       doctype="Journal Entry",
       filters="posting_date:>=:[start_date],posting_date:<=:[end_date],company:[company]",
       fields="name,posting_date,total_debit,total_credit,accounts"
   )
   ```
3. Filter to only journal entries that have the credit card liability account (2151-WCLI or 2151-WCLC)
4. Sum the credits to the liability account (should match Bill.com total)

**Report**:
```
📊 Reconciliation Summary

Bill.com Transactions: $XX,XXX.XX
ERPNext Journal Entries: $XX,XXX.XX
Difference: $X.XX

Status: ✅ Reconciled / ⚠️ Out of Balance
```

If out of balance by more than $1.00, list the discrepancies and suggest next steps.

## Error Handling

Throughout the process:
- Handle pagination carefully (Bill.com may return partial results)
- Check for API errors and report clearly
- Validate GL account codes exist before posting
- Handle multi-entity mismatches gracefully
- Provide actionable error messages

## Example Session

```
User: Sync last week's Bill.com transactions to ERPNext

Claude: I'll help you sync Bill.com credit card transactions to ERPNext.

Which company would you like to process?
1. Wash Cycle Laundry Inc. (WCLI)
2. WCL Chelsea LLC (WCLC)

User: 1

Claude: Processing Wash Cycle Laundry Inc. (WCLI)

What date range? (Default: last week, 2024-11-11 to 2024-11-17)

User: [Enter to accept default]

Claude: Fetching cleared transactions from Bill.com...
[Calls list_transactions_enriched for WCLI]

Found 47 transactions totaling $8,234.56

Enriching with employee data...
[Looks up employees in ERPNext]

Applying classification rules...
[Loads DMN rules, applies logic, uses LLM for non-matches]

Here are the results:

✅ AUTO_POST - High Confidence (38 transactions, $6,891.23)
[Lists transactions grouped by GL account]

⚠️ REVIEW - Needs Confirmation (7 transactions, $1,143.33)
[Lists with alternatives]

🚩 REJECTED - Manual Handling Required (2 transactions, $200.00)
[Lists with reasons]

Ready to review the items needing confirmation?

[User reviews and confirms/adjusts classifications]

Creating 45 journal entries in ERPNext...
✅ Created JE-WCLI-2024-00123 for Amazon - $45.67
✅ Created JE-WCLI-2024-00124 for Shell - $78.90
[...]

📊 Reconciliation Summary
Bill.com: $8,034.56 (45 transactions)
ERPNext: $8,034.56 (45 journal entries)
Difference: $0.00
Status: ✅ Reconciled

Sync complete!
```

## Files in This Skill

- **SKILL.md** (this file): Main instructions
- **dmn_rules.csv**: Deterministic classification rules (human-editable CSV)
- **classification_rules.jdm.json**: Compiled rules in GoRules JDM format (auto-generated)
- **classify_transaction.py**: Python classifier script using ZEN engine
- **convert_dmn_to_jdm.py**: Converts CSV rules to JDM format
- **journal_entry_template.py**: Standardized Journal Entry template for ERPNext
- **chart_of_accounts.json**: Account definitions, MCC mappings, and classification philosophy
- **requirements.txt**: Python dependencies
- **.venv/**: Python virtual environment with zen-engine

## Key MCP Tools Used

### Bill.com MCP Server
- `list_transactions_enriched`: Fetch transactions with budget/user names
- `get_transaction`: Get detailed transaction info (if needed)

### Frappe MCP Server
- `list_documents`: Query employees, accounts, journal entries
- `create_document`: Create journal entries
- `get_doctype_schema`: Get account structure (if needed)

## Tips for Success

1. **Always handle pagination** - Bill.com may split results across multiple pages
2. **Validate accounts exist** - Check GL account codes before posting
3. **Use transaction date** - Post with `occurredTime` not current date
4. **Be consistent** - Same transaction types should always map to same accounts
5. **Save state** - If interrupted, be able to resume without duplicating work
6. **Clear reporting** - User should always know what's happening and why

## Customization

Users can customize classification by:
1. **Editing dmn_rules.csv** - Add/modify deterministic rules (run convert_dmn_to_jdm.py after changes)
2. **Updating chart_of_accounts.json** - Refine account descriptions and classification philosophy
3. **Adjusting confidence thresholds** - Change when to auto-post vs. review

The skill will automatically pick up changes to these files on next run.
