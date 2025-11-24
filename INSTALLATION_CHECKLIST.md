# Installation Checklist

Use this checklist to ensure proper installation and configuration of the Bill.com to ERPNext sync skill.

## Pre-Installation Requirements

### Required MCP Servers

- [ ] **Bill.com MCP Server** is running
  - [ ] Environment variable `BILL_API_TOKEN_INC` set (for WCLI)
  - [ ] Environment variable `BILL_API_TOKEN_CHL` set (for WCLC)
  - [ ] Base URL configured: `https://gateway.stage.bill.com/connect`
  - [ ] Server accessible via MCP protocol

- [ ] **Frappe MCP Server** is running
  - [ ] Environment variable `FRAPPE_API_KEY` set
  - [ ] Environment variable `FRAPPE_API_SECRET` set
  - [ ] Environment variable `FRAPPE_BASE_URL` set
  - [ ] Server accessible via MCP protocol

### Verify MCP Server Tools

Test that required tools are available:

**Bill.com MCP Server**:
```bash
# Should list these tools:
- list_transactions_enriched
- list_transactions
- get_transaction
- list_budgets
- list_budget_users
```

**Frappe MCP Server**:
```bash
# Should list these tools:
- list_documents
- create_document
- get_document
- update_document
- get_doctype_schema
```

## Installation Steps

### 1. Choose Installation Location

Select one:

- [ ] **User Skills Directory**
  ```bash
  mkdir -p ~/.config/claude/skills/billcom-erpnext-sync
  ```

- [ ] **Centralized Skills** (if using /mnt/skills)
  ```bash
  mkdir -p /mnt/skills/user/billcom-erpnext-sync
  ```

### 2. Copy Skill Files

- [ ] Copy `SKILL.md` to installation directory
- [ ] Copy `dmn_rules.csv` to installation directory
- [ ] Copy `chart_of_accounts.json` to installation directory
- [ ] Copy `README.md` to installation directory (optional, for reference)
- [ ] Copy `DMN_REFERENCE.md` to installation directory (optional, for reference)
- [ ] Copy `QUICKSTART.md` to installation directory (optional, for reference)
- [ ] Copy `WORKFLOW_DIAGRAMS.md` to installation directory (optional, for reference)

**Required files** (minimum):
- SKILL.md
- dmn_rules.csv
- chart_of_accounts.json

**Optional files** (recommended for reference):
- README.md
- DMN_REFERENCE.md
- QUICKSTART.md
- WORKFLOW_DIAGRAMS.md

### 3. Verify File Permissions

```bash
# Files should be readable
ls -la [installation-directory]/
# Output should show rw-r--r-- permissions
```

- [ ] All files are readable
- [ ] No permission errors

## Configuration Verification

### 4. Verify Company Configuration

In ERPNext, confirm:

- [ ] Company "Wash Cycle Laundry Inc." exists
- [ ] Company "WCL Chelsea LLC" exists
- [ ] Account "2151 - Divvy Credit Card - WCLI" exists for WCLI
- [ ] Account "2151 - Divvy Credit Card - WCLC" exists for WCLC

### 5. Verify Chart of Accounts

Check that GL accounts in `dmn_rules.csv` exist in ERPNext:

Common accounts to verify:
- [ ] 5110 - Gas Tolls Fines
- [ ] 5120 - Vehicle Leases Mileage
- [ ] 5130 - Delivery Subcontractors
- [ ] 5200 - Maintenance
- [ ] 5220 - Employee Food
- [ ] 5400 - Office Expenses
- [ ] 5660 - Shipping Supplies
- [ ] 5700 - Telephone Internet
- [ ] 5800 - Travel
- [ ] 5900 - Web Services

Run this query in ERPNext to check:
```sql
SELECT account_number, account_name 
FROM `tabAccount` 
WHERE company IN ('Wash Cycle Laundry Inc.', 'WCL Chelsea LLC')
AND is_group = 0
ORDER BY account_number;
```

### 6. Verify Employee Records

In ERPNext, confirm:

- [ ] Employee records exist for Bill.com users
- [ ] Each employee has `user_id` field populated (matches Bill.com email)
- [ ] Each employee is assigned to correct company (WCLI or WCLC)
- [ ] Department/designation fields are populated (for DMN matching)

### 7. Test MCP Connectivity

Test Bill.com MCP:
```bash
# Try listing recent transactions
# Should return data without errors
```

- [ ] Can fetch transactions from Bill.com
- [ ] Enriched data includes budget names and user emails

Test Frappe MCP:
```bash
# Try listing employees
# Should return employee records
```

- [ ] Can fetch employees from ERPNext
- [ ] Can fetch accounts from Chart of Accounts

## First Run Test

### 8. Test with Small Date Range

- [ ] Start Claude conversation
- [ ] Request: "Sync Bill.com transactions from [yesterday] to [yesterday] to ERPNext"
- [ ] Select company when prompted
- [ ] Verify skill loads DMN rules successfully
- [ ] Check that transactions are fetched
- [ ] Review classification results
- [ ] **DO NOT confirm posting yet** - just verify workflow works

### 9. Verify Classification Logic

From the test run, check:

- [ ] DMN rules are applied correctly
- [ ] Merchant patterns match as expected
- [ ] Travel detection works (LOCAL vs. OUT_OF_STATE)
- [ ] Employee data is enriched properly
- [ ] GL accounts in results are valid

### 10. Test Journal Entry Creation (Optional)

If comfortable:

- [ ] Run skill for a single transaction day
- [ ] Confirm posting when prompted
- [ ] Verify journal entry created in ERPNext
- [ ] Check posting date matches transaction date
- [ ] Verify debit/credit accounts are correct
- [ ] Run reconciliation check

## Post-Installation Customization

### 11. Review and Adjust DMN Rules

- [ ] Open `dmn_rules.csv`
- [ ] Review starter rules
- [ ] Add company-specific merchants
- [ ] Adjust amount thresholds if needed
- [ ] Save changes

### 12. Review Classification Philosophy

- [ ] Open `chart_of_accounts.json`
- [ ] Verify expense policy is current in the `classification_philosophy` section
- [ ] Add any missing account descriptions in the `accounts` section
- [ ] Save changes

### 13. Document Custom Rules

Create a log of custom rules you add:

```markdown
## Custom DMN Rules Log

### 2024-11-22
- Added Amazon office supplies rule
- Adjusted Grainger amount thresholds

### [Future Date]
- [Your changes here]
```

## Troubleshooting

If any step fails, check:

### MCP Server Issues
- [ ] Servers are running
- [ ] Environment variables are set correctly
- [ ] Network connectivity is working
- [ ] API credentials are valid and not expired

### File Issues
- [ ] Files are in correct location
- [ ] Files have correct permissions
- [ ] CSV file has no syntax errors
- [ ] Markdown files are valid UTF-8

### ERPNext Issues
- [ ] Companies exist in ERPNext
- [ ] GL accounts exist and are active
- [ ] Employees exist with user_id set
- [ ] API user has permission to create Journal Entries

### Bill.com Issues
- [ ] API tokens are valid
- [ ] Correct environment (sandbox vs. production)
- [ ] Transactions exist in date range
- [ ] Transactions are in CLEAR status

## Support Resources

If you encounter issues:

1. **Check error messages** - They're designed to be actionable
2. **Review README.md** - Comprehensive troubleshooting section
3. **Check QUICKSTART.md** - Common first-time issues
4. **Review DMN_REFERENCE.md** - Rule syntax help
5. **Test MCP servers independently** - Isolate the issue

## Success Criteria

Installation is complete and successful when:

- [x] All required files are in place
- [x] MCP servers are accessible
- [x] Test run completes without errors
- [x] Classifications look reasonable
- [x] Can create journal entries (if tested)
- [x] Reconciliation check passes (if tested)

## Ready for Production

Before using in production:

- [ ] Test with 1 week of historical data
- [ ] Review all classifications carefully
- [ ] Verify journal entries are correct
- [ ] Reconciliation passes
- [ ] Document any custom rules added
- [ ] Train team members on review process

## Maintenance Checklist

After initial setup, maintain the skill:

**Weekly**:
- [ ] Process transactions
- [ ] Review REVIEW items for patterns
- [ ] Add new DMN rules as needed

**Monthly**:
- [ ] Audit AUTO_POST accuracy
- [ ] Update narrative rules if policy changes
- [ ] Check for new expense types

**Quarterly**:
- [ ] Full review of DMN rules
- [ ] Remove obsolete rules
- [ ] Update amount thresholds
- [ ] Review skill performance metrics

---

## Sign-Off

Installation completed by: ________________

Date: ________________

Notes:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
