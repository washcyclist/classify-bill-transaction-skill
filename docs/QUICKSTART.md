# Quick Start Guide

Get up and running with the Bill.com to ERPNext sync skill in 5 minutes.

## Prerequisites

- [ ] Bill.com Spend & Expense MCP server running
- [ ] Frappe (ERPNext) MCP server running
- [ ] Python 3.8+ installed
- [ ] Claude Code with skills enabled

## Installation (2 minutes)

### 1. Copy Skill Files

Copy these files to your Claude skills directory:

```bash
mkdir -p ~/.config/claude/skills/billcom-erpnext-sync
cd ~/.config/claude/skills/billcom-erpnext-sync

# Required files (9 total):
# - SKILL.md                          (Claude's main instructions)
# - chart_of_accounts.json            (Account definitions & classification philosophy)
# - dmn_rules.csv                     (Editable classification rules)
# - classification_rules.jdm.json     (Compiled rules, auto-generated)
# - classify_transaction.py           (Classification script)
# - journal_entry_template.py         (Journal entry formatter)
# - convert_dmn_to_jdm.py            (Rule compiler)
# - requirements.txt                  (Python dependencies)
# - .venv/                            (Virtual environment - will be created)
```

### 2. Setup Python Environment

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

This installs `zen-engine` for deterministic rule execution.

### 3. Test the Setup

```bash
# Test classification
.venv/bin/python3 classify_transaction.py \
  --transaction '{"merchantCategoryCode":"5541","rawMerchantName":"SHELL","amount":60,"state_match":"LOCAL"}' \
  --employee '{"team":"Delivery"}' \
  --billcom_budget "Gas"

# Test journal entry template
.venv/bin/python3 journal_entry_template.py \
  --transaction '{"id":"test123","merchantName":"Shell","amount":60,"occurredTime":"2024-11-20T10:00:00","authorizedTime":"2024-11-20T09:55:00","isCredit":false}' \
  --classification '{"gl_account":"Gas and Tolls","gl_account_name":"Gas and Tolls"}' \
  --company WCLI
```

Both should return valid JSON.

## First Run (2 minutes)

Start a conversation with Claude:

```
Sync last week's Bill.com transactions to ERPNext
```

Claude will:
1. Ask which company (WCLI or WCLC)
2. Confirm date range (default: last week)
3. Fetch and classify transactions using DMN rules + LLM
4. Present results grouped by confidence level
5. Create journal entries after confirmation
6. Run reconciliation

## Understanding Results

### ✅ AUTO_POST - High Confidence
- Matched DMN rule OR LLM >90% confidence
- Will auto-create journal entries after confirmation

### ⚠️ REVIEW - Medium Confidence
- LLM 70-90% confidence OR DMN rule marked REVIEW
- You must confirm or specify different account

### 🚩 REJECTED - Manual Handling
- Potential assets, multi-entity mismatches, policy violations
- Must handle manually outside this workflow

## Customizing Classification Rules

Edit `dmn_rules.csv` to add patterns:

```csv
merchant_pattern,merchant_category,amount_min,amount_max,user_team,state_match,gl_account,gl_account_name,action,notes
*USPS*,,,,,,,5660,Shipping Supplies,AUTO_POST,Postal shipping
*Shell*,5541,,,,Delivery,,Gas and Tolls,Gas and Tolls,AUTO_POST,Delivery gas
```

After editing, regenerate the compiled rules:

```bash
.venv/bin/python3 convert_dmn_to_jdm.py
```

## Files Explanation

| File | Purpose | Can Delete? |
|------|---------|-------------|
| **SKILL.md** | Claude's instructions | ❌ Required |
| **chart_of_accounts.json** | Account definitions & philosophy | ❌ Required |
| **dmn_rules.csv** | Editable classification rules | ❌ Required |
| **classification_rules.jdm.json** | Compiled rules (auto-gen) | ❌ Required |
| **classify_transaction.py** | Classification script | ❌ Required |
| **journal_entry_template.py** | JE formatter | ❌ Required |
| **convert_dmn_to_jdm.py** | Rule compiler | ❌ Required |
| **requirements.txt** | Python dependencies | ❌ Required |
| **.venv/** | Python virtual environment | ❌ Required |
| **README.md** | User documentation | ✅ Optional (for humans) |
| **DMN_REFERENCE.md** | Rule writing guide | ✅ Optional (for humans) |
| **QUICKSTART.md** | This file | ✅ Optional (for humans) |
| **test_classifications.py** | Testing script | ✅ Optional (development only) |

## Common Issues

### "zen-engine not found"
```bash
.venv/bin/pip install zen-engine
```

### "classification_rules.jdm.json not found"
```bash
.venv/bin/python3 convert_dmn_to_jdm.py
```

### "No transactions found"
- Check date range - transactions must be in CLEAR status
- Verify Bill.com MCP server credentials

### "Employee not found"
- Bill.com userEmail must match ERPNext Employee.user_id field

### Many transactions going to REVIEW
- **This is normal initially!**
- Add DMN rules for common patterns
- Target: 80-90% AUTO_POST after 2-4 weeks

## Pro Tips

1. **Start small**: Process one week, not months of backlog
2. **Build rules gradually**: Add patterns as you see them repeat
3. **Review carefully at first**: Trust builds over time
4. **Always reconcile**: Catches mistakes automatically
5. **Use batch mode**: More efficient for 20+ transactions

```
# Batch example (more efficient)
.venv/bin/python3 classify_transaction.py --batch '[
  {"transaction": {...}, "employee": {...}, "billcom_budget": "..."},
  {"transaction": {...}, "employee": {...}, "billcom_budget": "..."}
]'
```

## Success Metrics (After 1 Month)

- ⏱️ **Time savings**: 60-80% reduction in manual work
- ✅ **Accuracy**: 95%+ correct classifications
- 📊 **Coverage**: 80%+ transactions auto-classified
- 🔄 **Reconciliation**: Clean match every time

## Need Help?

1. Check error messages (designed to be actionable)
2. Review SKILL.md for detailed workflow steps
3. Check chart_of_accounts.json for account definitions
4. Test with small date ranges first

## Ready!

```
Sync last week's Bill.com transactions to ERPNext
```
