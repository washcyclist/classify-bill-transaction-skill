# Quick Start Guide

Get up and running with the Bill.com to ERPNext sync skill in 5 minutes.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Bill.com Spend & Expense MCP server running
- [ ] Frappe (ERPNext) MCP server running
- [ ] API credentials configured for both systems
- [ ] Access to Claude with skills enabled

## Installation (1 minute)

### Option 1: User Skills Directory
```bash
mkdir -p ~/.config/claude/skills/billcom-erpnext-sync
cd ~/.config/claude/skills/billcom-erpnext-sync

# Copy the 5 skill files here:
# - SKILL.md
# - dmn_rules.csv
# - chart_of_accounts.json
# - README.md
# - DMN_REFERENCE.md
```

### Option 2: Centralized Skills (if using /mnt/skills)
```bash
mkdir -p /mnt/skills/user/billcom-erpnext-sync
cd /mnt/skills/user/billcom-erpnext-sync

# Copy the 5 skill files here
```

## First Run (2 minutes)

### 1. Start a Conversation with Claude

```
I need to sync Bill.com credit card transactions to ERPNext
```

### 2. Follow the Prompts

Claude will ask:
1. **Which company?** Choose WCLI or WCLC
2. **Date range?** Press Enter for last week or specify dates

### 3. Review Classifications

Claude will show three groups:
- ✅ **AUTO_POST**: High confidence - will auto-create journal entries
- ⚠️ **REVIEW**: Needs your confirmation
- 🚩 **REJECTED**: Handle manually

### 4. Confirm and Post

- Review the REVIEW items and confirm/adjust
- Confirm you're ready to post
- Claude creates journal entries
- Reconciliation runs automatically

## Your First Customization (2 minutes)

### Add a Common Rule

Let's say you frequently buy supplies from Amazon for the office:

1. Open `dmn_rules.csv` in a spreadsheet or text editor

2. Add this line at the end:
```csv
*Amazon*,,,,,,Office Supplies,,,5400,Office Expenses,AUTO_POST,Amazon office supplies per user classification
```

3. Save the file

4. Next time you run the skill, Amazon purchases classified as "Office Supplies" in Bill.com will auto-post to account 5400

## Understanding Your First Results

### Example Output

```
Processing Wash Cycle Laundry Inc...
Found 23 transactions totaling $3,456.78

✅ AUTO_POST (20 transactions, $3,100.00)
1. 2024-11-15 - Shell - $45.67
   User: driver@wcl.com | Budget: Delivery Operations
   Classification: 5110 - Gas Tolls Fines
   Rule: Gas for delivery vehicles

2. 2024-11-16 - USPS - $12.50
   [...]

⚠️ REVIEW (3 transactions, $356.78)
1. 2024-11-16 - Home Depot - $250.00
   User: maintenance@wcl.com | Budget: Maintenance
   
   Suggested: 5200 - Maintenance
   Confidence: 85%
   
   Alternatives:
   - 5200 - Maintenance: Standard supplies
   - ASSET - Equipment: If specialized tool
   
   Please confirm or specify correct account.
```

### What to Check

**✅ AUTO_POST Items**:
- Skim through to make sure classifications look reasonable
- If something looks wrong, stop and adjust the DMN rule

**⚠️ REVIEW Items**:
- These need your explicit confirmation
- Choose the suggested account or provide a different one
- Common reasons: unusual amounts, new merchants, ambiguous purpose

**🚩 REJECTED Items**:
- These won't be posted automatically
- Handle in ERPNext manually
- Common reasons: potential assets (>$5k), multi-entity mismatches

## Common First-Time Issues

### "No transactions found"
**Fix**: Check your date range. Bill.com might not have cleared transactions yet.

### "Employee not found for email@domain.com"
**Fix**: Create the employee record in ERPNext or update the email to match.

### "GL Account 5400 not found"
**Fix**: Check account numbers in `dmn_rules.csv` match your Chart of Accounts.

### Many transactions going to REVIEW
**This is normal!** Your DMN rules file has starter rules, but you'll need to add more as you see patterns. Each time you run the skill:
1. Note which merchants/patterns go to REVIEW
2. Add appropriate DMN rules
3. Next time those will AUTO_POST

## Next Steps

### Week 1: Learning Mode
- Run the skill weekly
- Let most things go to REVIEW
- Add DMN rules for patterns you see repeatedly
- Get comfortable with the classifications

### Week 2-4: Building Coverage
- You should start seeing 60-70% AUTO_POST
- Add rules for your most common merchants
- Refine amount thresholds
- Build trust in the automation

### Month 2+: Production Mode
- Target 80-90% AUTO_POST
- Only edge cases go to REVIEW
- Quick weekly processing
- Consistent, accurate books

## Help & Resources

### Quick Reference
- **README.md** - Full documentation
- **DMN_REFERENCE.md** - How to create rules
- **chart_of_accounts.json** - Account definitions & expense policy guidance
- **SKILL.md** - Technical details (for Claude)

### Getting Support
1. Check error messages - they're designed to be actionable
2. Review the README troubleshooting section
3. Check DMN_REFERENCE for rule syntax
4. Test changes with small date ranges first

## Pro Tips

1. **Start with one week**: Don't try to process months of backlog initially
2. **Review carefully at first**: Trust builds over time
3. **Document weird cases**: Add notes to DMN rules for future reference
4. **Keep it simple**: Don't over-engineer rules - sometimes REVIEW is fine
5. **Reconcile always**: The reconciliation check catches mistakes

## Success Metrics

After your first month, you should see:
- ⏱️ **Time savings**: 60-80% reduction in manual categorization
- ✅ **Accuracy**: 95%+ correct classifications
- 📊 **Coverage**: 80%+ transactions auto-classified
- 🔄 **Reconciliation**: Clean match every time

## Ready to Go!

You're all set. Open Claude and try:

```
Sync last week's Bill.com transactions to ERPNext
```

The skill will guide you through the rest!
