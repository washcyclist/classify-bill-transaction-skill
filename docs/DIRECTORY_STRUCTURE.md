# Recommended Directory Structure

## Proposed Layout

```
billcom-erpnext-sync/
├── SKILL.md                          # Claude's main instructions (REQUIRED)
├── requirements.txt                  # Python dependencies (REQUIRED)
│
├── config/                           # Configuration files (REQUIRED)
│   ├── chart_of_accounts.json       # Account definitions & philosophy
│   ├── dmn_rules.csv                # Human-editable classification rules
│   └── classification_rules.jdm.json # Compiled rules (auto-generated)
│
├── scripts/                          # Executable Python scripts (REQUIRED)
│   ├── classify_transaction.py      # Classification engine
│   ├── journal_entry_template.py    # Journal entry formatter
│   └── convert_dmn_to_jdm.py        # Rule compiler
│
├── .venv/                            # Python virtual environment (REQUIRED)
│
├── docs/                             # Human documentation (OPTIONAL)
│   ├── README.md                     # User setup guide
│   ├── QUICKSTART.md                 # Getting started guide
│   └── DMN_REFERENCE.md              # DMN rule writing guide
│
└── tests/                            # Development/testing (OPTIONAL)
    └── test_classifications.py       # Test script
```

## Rationale

### Root Level (Core Files)
- **SKILL.md** - Must be at root so Claude finds it easily
- **requirements.txt** - Standard Python location
- **.venv/** - Standard Python virtual environment location

### `config/` Directory
**Purpose**: All configuration files that define business logic

- **chart_of_accounts.json** - Account structure and classification philosophy
- **dmn_rules.csv** - Human-editable rules (users will modify this frequently)
- **classification_rules.jdm.json** - Machine-generated, auto-synced from CSV

**Why separate**:
- Groups all business logic configuration
- Makes it clear these are customizable
- Easy to back up or version control separately

### `scripts/` Directory
**Purpose**: All executable Python scripts

- **classify_transaction.py** - Core classification engine
- **journal_entry_template.py** - Journal entry generation
- **convert_dmn_to_jdm.py** - Rule compilation utility

**Why separate**:
- Clear distinction between "code" and "config"
- Makes it obvious these are executables
- Could add more scripts without cluttering root

### `docs/` Directory
**Purpose**: Human-readable documentation

- **README.md** - Full setup and usage guide
- **QUICKSTART.md** - Quick getting started
- **DMN_REFERENCE.md** - Detailed rule writing guide

**Why separate**:
- Clearly optional (can delete entire directory)
- Doesn't clutter the core skill files
- Standard convention (most projects have a docs/ folder)

### `tests/` Directory
**Purpose**: Testing and development files

- **test_classifications.py** - Automated testing
- Could add: test fixtures, sample data, etc.

**Why separate**:
- Clearly for development only
- Can be excluded from production deployments
- Standard Python convention

## Migration Plan

### Option A: Restructure Existing Directory

```bash
cd /Users/gm-personal/claude_skills/classifying-bill.com-expenses

# Create new directories
mkdir -p config scripts docs tests

# Move configuration files
mv chart_of_accounts.json config/
mv dmn_rules.csv config/
mv classification_rules.jdm.json config/

# Move scripts
mv classify_transaction.py scripts/
mv journal_entry_template.py scripts/
mv convert_dmn_to_jdm.py scripts/

# Move documentation
mv README.md docs/
mv QUICKSTART.md docs/
mv DMN_REFERENCE.md docs/
mv PROJECT_SUMMARY.md docs/
mv INSTALLATION_CHECKLIST.md docs/
mv WORKFLOW_DIAGRAMS.md docs/

# Move tests
mv test_classifications.py tests/

# Clean up
# (Keep SKILL.md, requirements.txt, .venv/ at root)
```

### Option B: Fresh Install Structure

For new installations, use this directory layout from the start:

```bash
mkdir -p ~/.config/claude/skills/billcom-erpnext-sync/{config,scripts,docs,tests}
cd ~/.config/claude/skills/billcom-erpnext-sync

# Copy files to appropriate directories
# SKILL.md → root
# config files → config/
# scripts → scripts/
# docs → docs/
# tests → tests/
```

## Required Updates After Restructure

### 1. Update SKILL.md References

**Line 207** (Step 5D):
```markdown
OLD: Load the chart of accounts and classification philosophy from `chart_of_accounts.json`
NEW: Load the chart of accounts and classification philosophy from `config/chart_of_accounts.json`
```

**Line 181** (Step 5C):
```markdown
OLD: The rules are stored in `classification_rules.jdm.json`
NEW: The rules are stored in `config/classification_rules.jdm.json`
```

**Line 189-190** (Step 5C):
```markdown
OLD: 1. Edit `dmn_rules.csv`
     2. Run `python3 convert_dmn_to_jdm.py`
NEW: 1. Edit `config/dmn_rules.csv`
     2. Run `python3 scripts/convert_dmn_to_jdm.py`
```

**Lines 134, 161, 360, 368** (Script execution):
```bash
OLD: .venv/bin/python3 classify_transaction.py
NEW: .venv/bin/python3 scripts/classify_transaction.py

OLD: .venv/bin/python3 journal_entry_template.py
NEW: .venv/bin/python3 scripts/journal_entry_template.py
```

### 2. Update Script Path References

**classify_transaction.py** - Line ~293:
```python
OLD: jdm_path = args.jdm or str(script_dir / 'classification_rules.jdm.json')
NEW: jdm_path = args.jdm or str(script_dir.parent / 'config' / 'classification_rules.jdm.json')
```

**convert_dmn_to_jdm.py** - Update input/output paths:
```python
OLD: dmn_csv = Path(__file__).parent / 'dmn_rules.csv'
     jdm_output = Path(__file__).parent / 'classification_rules.jdm.json'
NEW: config_dir = Path(__file__).parent.parent / 'config'
     dmn_csv = config_dir / 'dmn_rules.csv'
     jdm_output = config_dir / 'classification_rules.jdm.json'
```

### 3. Update QUICKSTART.md

Update the file list section to show the new structure:

```markdown
# Required files (9 total):
# - SKILL.md                                (Root: Claude's main instructions)
# - requirements.txt                        (Root: Python dependencies)
# - config/chart_of_accounts.json          (Account definitions)
# - config/dmn_rules.csv                   (Classification rules)
# - config/classification_rules.jdm.json   (Compiled rules)
# - scripts/classify_transaction.py        (Classification script)
# - scripts/journal_entry_template.py      (JE formatter)
# - scripts/convert_dmn_to_jdm.py         (Rule compiler)
# - .venv/                                  (Virtual environment)
```

## Benefits of This Structure

1. **Clarity**: Immediately obvious what's required vs optional
2. **Maintainability**: Easy to find and edit configuration files
3. **Cleanliness**: Root directory only has 3 items (SKILL.md, requirements.txt, .venv/)
4. **Scalability**: Can add more scripts, configs, or docs without cluttering
5. **Professional**: Follows standard project layout conventions
6. **Deployment**: Can easily package just `SKILL.md + config/ + scripts/ + .venv/` for production

## Minimal Deployment (Production)

For a clean production deployment, you only need:

```
billcom-erpnext-sync/
├── SKILL.md
├── requirements.txt
├── config/
│   ├── chart_of_accounts.json
│   ├── dmn_rules.csv
│   └── classification_rules.jdm.json
├── scripts/
│   ├── classify_transaction.py
│   ├── journal_entry_template.py
│   └── convert_dmn_to_jdm.py
└── .venv/
```

**Total**: 9 files + 1 directory = ~10 items at root level (clean!)

The `docs/` and `tests/` directories can be omitted entirely in production.
