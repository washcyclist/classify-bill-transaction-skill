# DMN Rules Reference Guide

This guide explains how to create and maintain DMN (Decision Model and Notation) rules for automated transaction classification.

## Overview

DMN rules provide deterministic, rule-based classification of credit card transactions. When a transaction matches ALL specified conditions in a rule, that rule's GL account and action are applied.

## Rule Structure

Each rule in `dmn_rules.csv` has the following columns:

### Input Conditions (Filters)

| Column | Type | Description | Examples |
|--------|------|-------------|----------|
| `merchant_pattern` | Wildcard | Matches merchant name (case-insensitive) | `*Amazon*`, `*USPS*`, `Shell*` |
| `merchant_category` | Exact | Bill.com MCC code | `5541` (gas stations), `5812` (restaurants) |
| `amount_min` | Number | Minimum transaction amount | `100`, `500`, `5000` |
| `amount_max` | Number | Maximum transaction amount | `50`, `500`, `5000` |
| `user_team` | Exact | Employee department | `Delivery`, `Admin`, `Production` |
| `user_city` | Exact | Employee city | `Philadelphia`, `Lynn` |
| `billcom_category` | Exact | User's classification in Bill.com | `Travel`, `Office`, `Maintenance` |
| `state_match` | Enum | Transaction location vs. home | `LOCAL`, `OUT_OF_STATE` |

### Output Actions

| Column | Type | Description |
|--------|------|-------------|
| `gl_account` | Code | Target GL account code (without company prefix) |
| `gl_account_name` | Text | Account name for reference |
| `action` | Enum | `AUTO_POST`, `REVIEW`, or `REJECT` |
| `notes` | Text | Explanation for documentation |

## Rule Matching Logic

### How Matching Works

A transaction matches a rule when **ALL specified conditions** are true:
- Empty/blank fields = "match any" (no filter)
- Each non-empty field must match exactly (or pass the wildcard pattern)
- First matching rule wins (rules are evaluated in order)

### Wildcard Patterns

Use `*` for wildcard matching in `merchant_pattern`:
- `*Amazon*` - matches any merchant with "Amazon" anywhere
- `Shell*` - matches merchants starting with "Shell"
- `*USPS` - matches merchants ending with "USPS"

Matching is **case-insensitive**: `*amazon*` matches "AMAZON", "Amazon.com", etc.

### Amount Ranges

Combine `amount_min` and `amount_max` for ranges:
- `amount_min=100, amount_max=500` - matches $100 to $500
- `amount_min=500, amount_max=` (blank) - matches $500 and up
- `amount_min=, amount_max=50` - matches up to $50

### State Matching

The skill automatically determines if a transaction is LOCAL or OUT_OF_STATE:
- **LOCAL**: Transaction state matches employee's home state
  - WCLI employees (Philly area) → PA is LOCAL
  - WCLC employees (Lynn area) → MA is LOCAL
- **OUT_OF_STATE**: Any other state

Use this to distinguish:
- Local parking → Gas/Tolls account
- Travel parking → Travel account

## Actions

### AUTO_POST
- High confidence classification
- Will be posted automatically after user confirmation
- Use for well-established patterns

### REVIEW
- Requires user confirmation before posting
- Use for edge cases or amounts that need oversight
- Presents suggested account but asks for confirmation

### REJECT
- Transaction excluded from automatic processing
- Must be handled manually
- Use for potential assets, errors, or policy violations

## Common Patterns

### 1. Simple Merchant Match
Match all transactions from a specific merchant:

```csv
*USPS*,,,,,,,,,5660,Shipping Supplies,AUTO_POST,All USPS purchases
```

### 2. Amount-Based Rules
Different accounts based on transaction size:

```csv
*Grainger*,,,0,500,,,,,5200,Maintenance,AUTO_POST,Small maintenance purchases
*Grainger*,,,500,5000,,,,,5200,Maintenance,REVIEW,Medium purchases - verify not equipment
*Grainger*,,,5000,,,,,,ASSET,REJECT,Large purchase - likely asset
```

### 3. Team-Based Classification
Same merchant, different accounts by team:

```csv
*Shell*,5541,,,,Delivery,,,5110,Gas Tolls Fines,AUTO_POST,Gas for delivery vehicles
*Shell*,5541,,,,Admin,,,5800,Travel,AUTO_POST,Gas for admin travel
```

### 4. Location-Based Rules
Local vs. travel expenses:

```csv
*Restaurant*,5812,,,,,,,LOCAL,5220,Employee Food,AUTO_POST,Local restaurant
*Restaurant*,5812,,,,,,,OUT_OF_STATE,5800,Travel,AUTO_POST,Restaurant during travel
*Parking*,,,,,,,,LOCAL,5110,Gas Tolls Fines,AUTO_POST,Local parking
*Parking*,,,,,,,,OUT_OF_STATE,5800,Travel,AUTO_POST,Travel parking
```

### 5. User Classification Hint
Trust user's classification in Bill.com:

```csv
*Amazon*,,,,,,Office,,,5400,Office Expenses,AUTO_POST,User classified as office
*Amazon*,,,,,,Maintenance,,,5200,Maintenance,AUTO_POST,User classified as maintenance
```

### 6. Merchant Category Code (MCC)
Use industry codes for broad categories:

```csv
,5541,,,,Delivery,,,5110,Gas Tolls Fines,AUTO_POST,Any gas station for delivery
,7011,,,,,,,OUT_OF_STATE,5800,Travel,AUTO_POST,Any hotel during travel
,5812,,,,,,,LOCAL,5220,Employee Food,AUTO_POST,Any restaurant - local
```

Common MCCs:
- `5541` - Gas stations
- `5812` - Restaurants
- `7011` - Hotels
- `7512` - Car rentals
- `5942` - Book stores
- `5999` - Miscellaneous retail

## Best Practices

### Rule Ordering
- **Specific rules first**: More specific rules should come before general ones
- **Amount-based progression**: List rules from smallest to largest amounts
- Example:
  ```csv
  *Grainger*,,,0,500,,,,,5200,Maintenance,AUTO_POST,Small
  *Grainger*,,,500,5000,,,,,5200,Maintenance,REVIEW,Medium  
  *Grainger*,,,5000,,,,,,ASSET,REJECT,Large
  ```

### Maintainability
- **Clear notes**: Always explain why the rule exists
- **Consistent patterns**: Use similar logic for similar merchants
- **Regular review**: Check REVIEW transactions for new patterns to add

### Testing New Rules
1. Add the rule to `dmn_rules.csv`
2. Run classification on historical transactions
3. Review what the rule matches
4. Adjust conditions if needed
5. Move from REVIEW to AUTO_POST once confident

### Avoiding Conflicts
- Test new rules against existing ones
- Use `action=REVIEW` initially for new patterns
- More specific rules override general ones (first match wins)

## Examples by Use Case

### Delivery Operations
```csv
*Shell*,5541,,,,Delivery,,,5110,Gas Tolls Fines,AUTO_POST,Delivery gas
*Exxon*,5541,,,,Delivery,,,5110,Gas Tolls Fines,AUTO_POST,Delivery gas
*Uber*,,,,,Delivery,,,5130,Delivery Subcontractors,AUTO_POST,Uber for deliveries
*Lyft*,,,,,Delivery,,,5130,Delivery Subcontractors,AUTO_POST,Lyft for deliveries
*EZPass*,,,,,Delivery,,,5110,Gas Tolls Fines,AUTO_POST,Delivery tolls
```

### Admin/Overhead Operations
```csv
*Zoom*,,,,,,,,,5900,Web Services,AUTO_POST,Video conferencing
*Slack*,,,,,,,,,5900,Web Services,AUTO_POST,Team communication
*Google*,,,,,,,,,5900,Web Services,AUTO_POST,Google services
*LinkedIn*,,,,,,,,,5900,Web Services,AUTO_POST,LinkedIn services
*Office Depot*,,,,,,,,,5400,Office Expenses,AUTO_POST,Office supplies
```

### Travel
```csv
*Hotel*,7011,,,,,,,OUT_OF_STATE,5800,Travel,AUTO_POST,Hotels
*Hertz*,7512,,,,,,,OUT_OF_STATE,5800,Travel,AUTO_POST,Car rental - travel
*Uber*,,,,,Admin,,,5800,Travel,AUTO_POST,Uber for travel
*Restaurant*,5812,,0,50,,,,OUT_OF_STATE,5800,Travel,AUTO_POST,Meals under $50
*Restaurant*,5812,,50,,,,,OUT_OF_STATE,5800,Travel,REVIEW,Meals over $50
```

### Maintenance
```csv
*Home Depot*,,,0,150,,,,,5200,Maintenance,AUTO_POST,Small purchases
*Home Depot*,,,150,500,,,,,5200,Maintenance,REVIEW,Medium - verify not furniture
*Lowes*,,,0,150,,,,,5200,Maintenance,AUTO_POST,Small purchases
*Grainger*,,,0,500,,,,,5200,Maintenance,AUTO_POST,Supplies and parts
```

## Troubleshooting

### Rule Not Matching
1. Check merchant name exactly as it appears in Bill.com
2. Verify wildcard pattern includes the right text
3. Ensure all specified conditions can be met simultaneously
4. Remember: blank = "any", so leaving fields empty makes matching easier

### Wrong Account Selected
1. Check rule order - first match wins
2. Look for overlapping conditions with other rules
3. Make specific rules come before general ones
4. Use REVIEW action to validate before making AUTO_POST

### Too Many REVIEWs
- Add more specific rules for common patterns
- Use broader merchant patterns with wildcards
- Consider using MCC codes for category-level rules
- Review last 2-3 weeks of transactions for patterns

## Maintenance Schedule

**Weekly**: Review REVIEW transactions for new patterns
**Monthly**: Audit AUTO_POST accuracy  
**Quarterly**: Full review of all rules for relevance
**Annually**: Clean up unused rules

## Getting Help

If you're unsure about a classification:
1. Check the narrative_rules.md for policy guidance
2. Look at historical transactions for similar purchases
3. Use REVIEW action to validate before auto-posting
4. Ask the accounting team for guidance on edge cases
