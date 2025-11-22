# Bill.com to ERPNext Credit Card Sync Skill

This Claude skill automates the classification and posting of credit card transactions from Bill.com Spend & Expense to ERPNext using a combination of deterministic rules and AI-powered classification.

## What This Skill Does

1. **Fetches** cleared credit card transactions from Bill.com for a specified date range
2. **Enriches** transactions with employee information from ERPNext
3. **Classifies** transactions using:
   - DMN (Decision Model and Notation) rules for deterministic matching
   - LLM-based classification for complex cases
4. **Presents** all transactions grouped by confidence level for review
5. **Creates** journal entries in ERPNext after confirmation
6. **Reconciles** totals between Bill.com and ERPNext

## Setup

### 1. Prerequisites

You need:
- Bill.com Spend & Expense account with API access (credentials in MCP server)
- ERPNext instance with API access (credentials in MCP server)
- Both MCP servers configured and running:
  - Bill.com MCP Server (`billcom-server.py`)
  - Frappe MCP Server (`frappe-mcp-server`)

### 2. Install This Skill

Copy these files to your Claude skills directory:

```
~/.config/claude/skills/billcom-erpnext-sync/
├── SKILL.md              (main skill instructions)
├── dmn_rules.csv         (classification rules - editable)
├── narrative_rules.md    (expense policy guidance)
└── README.md             (this file)
```

OR for centralized skills:

```
/mnt/skills/user/billcom-erpnext-sync/
├── SKILL.md
├── dmn_rules.csv
├── narrative_rules.md
└── README.md
```

### 3. Verify MCP Servers

Ensure both MCP servers are accessible and have the required tools:

**Bill.com MCP Server** should have:
- `list_transactions_enriched`
- `get_transaction`

**Frappe MCP Server** should have:
- `list_documents`
- `create_document`
- `get_doctype_schema`

## Configuration

### Companies

The skill is configured for two entities:

| Company | Bill.com Parameter | Credit Card Account | Home Base |
|---------|-------------------|---------------------|-----------|
| Wash Cycle Laundry Inc. | "Wash Cycle Laundry Inc." | 2151 - Divvy Credit Card - WCLI | Philadelphia, PA |
| WCL Chelsea LLC | "WCL Chelsea LLC" | 2151 - Divvy Credit Card - WCLC | Lynn, MA |

### DMN Rules

Edit `dmn_rules.csv` to customize classification rules. The file has these columns:

- **merchant_pattern**: Wildcard match for merchant name (e.g., `*Amazon*`)
- **merchant_category**: Bill.com MCC code filter
- **amount_min/max**: Amount range filters
- **user_team**: Employee department filter
- **user_city**: Employee location filter
- **billcom_category**: User's Bill.com classification
- **state_match**: `LOCAL` or `OUT_OF_STATE`
- **gl_account**: Target GL account code
- **gl_account_name**: Account name (for reference)
- **action**: `AUTO_POST`, `REVIEW`, or `REJECT`
- **notes**: Explanation of the rule

**Empty fields** mean "match any value" (no filter applied).

**Example Rules**:
```csv
*USPS*,,,,,,,,,5660,Shipping Supplies,AUTO_POST,Postal shipping
*Shell*,5541,,,,Delivery,,,5110,Gas Tolls Fines,AUTO_POST,Gas for delivery
*Shell*,5541,,,,Admin,,,5800,Travel,AUTO_POST,Gas for admin travel
```

### Narrative Rules

The `narrative_rules.md` file contains your expense classification policy. Claude uses this for non-DMN classifications. Update this file to refine AI classification behavior.

## Usage

### Basic Usage

In Claude:

```
Sync last week's Bill.com transactions to ERPNext
```

Claude will:
1. Ask which company to process
2. Confirm date range (defaults to last week)
3. Fetch and classify transactions
4. Present results for review
5. Create journal entries after confirmation
6. Run reconciliation

### Specify Date Range

```
Sync Bill.com transactions from November 1-15 to ERPNext
```

### Process Both Companies

```
Sync Bill.com transactions for all companies for last week
```

## Understanding Results

### Transaction Classification

Transactions are grouped into three categories:

#### ✅ AUTO_POST - High Confidence
- Matched a DMN rule with `AUTO_POST` action
- OR LLM classified with >90% confidence
- Will be posted automatically after confirmation

#### ⚠️ REVIEW - Medium Confidence
- LLM classified with 70-90% confidence
- OR DMN rule marked as `REVIEW`
- Requires user confirmation or manual selection

#### 🚩 REJECTED - Manual Handling
- Potential asset purchases
- Multi-entity mismatches
- Other rule violations
- Must be handled outside this workflow

### Journal Entry Format

Each transaction creates a journal entry with:
- **Posting Date**: Transaction date from Bill.com (when it cleared)
- **Voucher Type**: Bank Entry
- **User Remark**: `[Merchant Name] - [Date]`
- **Accounts**:
  - Debit: Expense GL account (from classification)
  - Credit: Credit card liability account (2151-WCLI or 2151-WCLC)

Example:
```
JE-WCLI-2024-00123
Date: 2024-11-15
Remark: Amazon - 2024-11-15

Debit:  5400 - Office Expenses           $45.67
Credit: 2151 - Divvy Credit Card - WCLI  $45.67
```

## Reconciliation

After posting, the skill verifies:
- Sum of Bill.com transactions = Sum of ERPNext journal entry credits to liability account
- Reports any discrepancies > $1.00

If out of balance:
1. Check for duplicate postings
2. Verify all transactions were processed
3. Look for manual journal entries in the date range
4. Check for transactions with wrong posting dates

## Troubleshooting

### "No transactions found"
- Verify date range is correct
- Check Bill.com credentials are valid
- Ensure transactions are in CLEAR status (not pending)

### "Employee not found"
- Check that Bill.com userEmail matches ERPNext Employee.user_id
- Verify employee record exists in correct company

### "GL account not found"
- Check account code in dmn_rules.csv matches ERPNext Chart of Accounts
- Verify account exists for the selected company
- Account must not be a group account (must be a leaf account)

### "Multi-entity mismatch"
- Employee's company in ERPNext doesn't match selected Bill.com company
- May indicate transaction assigned to wrong user
- Handle manually or reassign in Bill.com

### Journal Entry Creation Failed
- Check ERPNext permissions for API user
- Verify posting date is not in a closed fiscal period
- Check account codes are valid and active

## Best Practices

### Regular Processing
- Process transactions weekly to maintain consistency
- Don't let unclassified transactions accumulate
- Keep DMN rules up to date as spending patterns change

### DMN Rule Maintenance
- Review REVIEW transactions for patterns
- Add new DMN rules for recurring transaction types
- Use `REVIEW` action for edge cases that need oversight
- Keep notes clear and descriptive

### Classification Quality
- If many transactions go to REVIEW, add more DMN rules
- If LLM classifications are consistently wrong, update narrative_rules.md
- Review rejected transactions to identify policy gaps

### Reconciliation
- Always run reconciliation after posting
- Investigate any discrepancies immediately
- Keep Bill.com and ERPNext posting dates aligned

## Customization

### Adding Custom Rules

To add a new DMN rule:
1. Open `dmn_rules.csv`
2. Add a new row with your conditions
3. Save the file
4. Next run will pick up the new rule

Example - classify Square payments as merchant fees:
```csv
*Square*,,,,,,,,,5300,Merchant Card Services,AUTO_POST,Square payment processing
```

### Adjusting Confidence Thresholds

To change when transactions auto-post vs. need review, edit the SKILL.md file:
- Current: >90% = AUTO_POST, 70-90% = REVIEW
- Adjust these percentages in Step 5D of SKILL.md

### Multi-Entity Support

To add a third company:
1. Update MCP server with new credentials
2. Add company mapping in SKILL.md Step 1
3. Add credit card liability account mapping
4. Add employee home base mapping

## Examples

### Example 1: Straightforward Week

```
User: Sync last week's transactions for WCLI

Processing Wash Cycle Laundry Inc...
Found 23 transactions totaling $3,456.78

✅ AUTO_POST (20 transactions, $3,100.00)
- Shell gas stations → 5110 Gas Tolls Fines
- USPS shipping → 5660 Shipping Supplies
- Office supply purchases → 5400 Office Expenses

⚠️ REVIEW (3 transactions, $356.78)
- Home Depot $250 - Suggested: 5200 Maintenance

Ready to post? Yes

Created 23 journal entries
✅ Reconciled - $3,456.78 = $3,456.78
```

### Example 2: Complex Classifications

```
User: Sync Nov 1-15 for WCLC

Processing WCL Chelsea LLC...
Found 45 transactions totaling $8,234.56

✅ AUTO_POST (35 transactions, $6,500.00)

⚠️ REVIEW (8 transactions, $1,534.56)
1. Grainger $450 - Medium purchase
   Suggested: 5200 Maintenance (85% confidence)
   Alternatives:
   - Could be small equipment if specialized tool
   
   Confirm? Yes

2. Hotel in Boston $300
   Suggested: 5800 Travel (MEDIUM confidence)
   Note: Employee is based in Lynn, MA (local)
   
   Actually local? Yes → Changed to 5220 Employee Food

[...]

🚩 REJECTED (2 transactions, $200.00)
- Grainger $5,500 - Over $5,000 threshold, likely equipment asset

Created 43 journal entries, skipped 2
✅ Reconciled
```

## Support

For issues:
1. Check MCP servers are running and accessible
2. Verify ERPNext and Bill.com credentials
3. Review error messages for specific issues
4. Check DMN rules syntax if classifications are wrong

## Version History

- **v1.0** (2024-11-22): Initial release
  - DMN-based deterministic classification
  - LLM fallback for complex cases
  - Multi-entity support
  - Automatic reconciliation

## License

This skill is part of the Wash Cycle Laundry internal tooling.
