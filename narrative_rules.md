The company's chart of accounts is the master list of how we classify all the movements of money in and out of the company. This is a guide to how we classify the expenses according to our account structure.

## MCC Codes: Your Most Reliable Classification Signal

**CRITICAL: Merchant Category Codes (MCC) are industry-standard codes assigned by payment networks. They are MORE RELIABLE than user-assigned Bill.com budgets.**

When classifying transactions, prioritize MCC codes over Bill.com budget names. Common MCC mappings:

### Transportation & Travel MCCs
| MCC | Description | GL Account | Notes |
|-----|-------------|------------|-------|
| 3000-3350 | Airlines | 5216 Travel Expenses | All airline MCCs map to travel |
| 4111 | Local transit (subway, bus) | 5216 Travel Expenses | MBTA, SEPTA, etc. |
| 4112 | Passenger railways | 5216 Travel Expenses | Amtrak |
| 4121 | Taxicabs/rideshare | 5216 Travel Expenses (Admin) or Subcontractor for Delivery | Context-dependent |
| 5541 | Service stations (gas) | Gas and Tolls (Delivery) or 5216 Travel Expenses (Admin) | NOT maintenance! |
| 7011 | Hotels/lodging | 5216 Travel Expenses | |
| 7512 | Car rental | Vehicle Lease and Mileage (Delivery) or 5216 Travel Expenses | Context-dependent |
| 7523 | Parking lots | Gas and Tolls (Delivery) or 5216 Travel Expenses | NOT maintenance! |

### Software & Technology MCCs
| MCC | Description | GL Account | Notes |
|-----|-------------|------------|-------|
| 5734 | Computer software stores | 5900 Web Services | SaaS subscriptions |
| 7372 | Computer programming | 5900 Web Services | GitHub, dev tools |
| 7379 | Computer services | 5900 Web Services | Cloud services |

### Shipping & Postal MCCs
| MCC | Description | GL Account | Notes |
|-----|-------------|------------|-------|
| 9402 | Postal services | 5660 Shipping | USPS - NOT travel! |
| 4215 | Courier services | 5660 Shipping | FedEx, UPS |

### Food & Restaurants MCCs
| MCC | Description | GL Account | Notes |
|-----|-------------|------------|-------|
| 5411 | Grocery stores | 5220 Employee Food (local) or 5800 Travel (out-of-state) | |
| 5812 | Restaurants | 5220 Employee Food (local) or 5800 Travel (out-of-state) | |
| 5814 | Fast food | 5220 Employee Food | |

### Office & Supplies MCCs
| MCC | Description | GL Account | Notes |
|-----|-------------|------------|-------|
| 5111 | Office supplies | 5400 Office Expenses | Staples, Office Depot |
| 5943 | Stationery stores | 5400 Office Expenses | |
| 6513 | Real estate | 5209 Office Rent | Regus, WeWork |

### Industry-Specific MCCs
| MCC | Description | GL Account | Notes |
|-----|-------------|------------|-------|
| 7211 | Dry cleaners/laundry | 5150 Coin Wash Fees | Revolution Laundry |
| 5968 | Subscription merchants | 5245 Professional Subscriptions | HBR, etc. |
| 8398 | Charitable organizations | 5020 Advertising Marketing | Usually sponsorships |
| 9399 | Government services | 5229 Business Taxes & Licenses | May also be 5206 Legal |

### Common Misclassification Patterns to Override

**ALWAYS override these Bill.com misclassifications:**

1. **Gas stations classified as "Maintenance"**: MCC 5541 = Gas, not maintenance
2. **Parking classified as "Maintenance"**: MCC 7523 = Parking, not maintenance
3. **Software classified as "Travel"**: MCC 5734/7372 = Web Services
4. **USPS classified as "Travel"**: MCC 9402 = Shipping
5. **Subscriptions classified as "Travel"**: MCC 5968 = Professional Subscriptions

---

### Key Principles: Consistency, Materiality, and Maintainability

As you’ll see below, classifying expenditures into accounts is part science, part art.== ====**There are definitely “wrong” answers, but sometimes there is more than one potentially “right” answer.**==== ==For example, a general manager might reasonably be classified as a “Cost of Sales” Laundry payroll expense (especially if they are the type of general manager who is often riding a truck or on the production line instead of behind a desk), but also might reasonably be classified as a “SG&A Payroll” overhead expense. However, certain things are always important:
- Consistency Over time. Some expenses might reasonably fit into 2 different accounts, but if it is a recurring expense, **whichever account we choose to use is the account we should stick with.** I.e., an expense might reasonable be classified in either “Account A” or “Account B,” but it’s a problem if we classify it in “Account A” in January and “Account B” in February.
- Materiality. As with all things, reality can get pretty complex. For example, perhaps Gabriel rents a car in Boston primarily to get around during his visit for sales and management purposes. However, during his 2-day visit, he spends an entire day using the car to make emergency drop-offs to customers instead. It may be more precise to allocate 50% to “Travel” and 50% to “Delivery Expenses,” but often these attempts to be very exact/precise lead to inconsistencies an errors that, as a whole, work against the accuracy/reliability/timeliness of our reports. And besides, a $40 allocation is not “material.” So in this case, if Gabriel’s rental car is usually attributed to “Travel,” it’s probably best to attribute it 100% to “Travel.”
### Top Level Question: Cost of Goods Sold, Overhead, or Balance Sheet Account?

The first big distinction is whether an expense is a Cost of Sales Expense, Overhead Expense, or Balance Sheet account. These are high-level groups of our expense accounts, and our profit and loss sums up expenses by these groups.
**One very important concept is that choosing the proper account is equal parts determining what the expense is FOR and what the expense IS. As examples:**
- If Gabriel rents a car on a site visit to Boston to visit customers or just to get around while traveling, it would be a Travel Expense (Travel is a OVERHEAD account).
- On the other hand, if somebody in Philadelphia rents a car as a backup/replacement to do deliveries, it is a Vehicle Leases expense (Vehicles are a COST OF SALES)
- On the other hand, if we make a loan payment to pay for a company vehicle that we own, that is a capital expenditure/BALANCE SHEET item.
- Similarly, if somebody buys tape to have around the office since sometimes people who work in offices need tape, that’s an “Office Supply” expense (which is an Overhead account)
- However, if somebody buys tape to seal packages we are sending to our customers, that’s a Misc Wash Costs expense (a Cost of Sales Account).
- If a maintenance worker goes to Grainger and buys $750 of screws, seals, lubricants, etc to help maintain or repair equipment, that is a Maintenance COST OF SALES. If he goes to Grainger and buys a $750 pump, that’s probably also a maintenance expense. If he goes to Grainger and buys a $5,500 pump, that’s probably an equipment ASSET (Balance Sheet Account).
Always be conscious about whether the account to which you assign an expense is a Cost of Sales, Overhead, or Balance Sheet account. Sometimes an account might have a title that seems like it fits (“They rented a car; it must be travel!, or It’s a Loan Payment for a Vehicle, it must be a Delivery Expense!), but the use of the car does not conform to the Cost of Sales / Overhead distinction.
#### Cost of Sales

Cost of Sales expenses are those expenses that have to do directly with the process of picking up, laundering, and dropping off our product to customers. Most, but not all, Cost of Sales expenses are variable costs, meaning that there’s a pretty direct relationship between the amount of laundry that we do and the size of Cost of Sales expenses.
Good examples of Cost of Sales expenses are:
- Detergents
- Utilities for the production plant
- Plant labor
- Rent for our production plant
#### Overhead

Overhead expenses are expenses related to the sales, general administrative, and marketing expense for managing the company. Many, but not all, administrative costs are somewhat fixed, meaning that, at least while our sales stay in the same ballpark, these costs don’t go up or down. Good examples of overhead expenses are:
- Accounting staff
- General business insurance
- Rent for office/administrative locations
#### Balance Sheet Accounts

Balance Sheet accounts are those accounts that have to do with the Assets and Liabilities of the company. Assets are those things we purchase that have enduring value that lasts over time, like vehicles we own, industrial equipment, and real estate. Assets must also have value that is “material” to the company (which is not precisely defined). They are also money that is owed back to us, like employee advances, or accounts receivable. Liabilities are debts of the company, whether loans, IOUs, payables, or many types of long term leases.
When we categorize a payment as going to an Asset (instead of an Expense), we say that it is a “Capital Expenditure” (not an Expense). Practically speaking, anything that we categorize as an “Asset” is something we must track and depreciate over time, and we have typically have been very limited in the things that we capitalize as assets because our ability to track assets, verify that we still have them, and then make appropriate depreciation schedules in our books is limited by our software and management capacity.
There are certain things that we MUST categorize as assets, like industrial equipment, vehicles, and real estate. Our policy has been to expense (rather than capitalize and hold as inventory) linen items, since they do not reliably last for longer than a year, and it is very hard to inventory them (they are also phantom assets, since they are worth basically nothing when used).
There are some judgment calls that we have made to EXPENSE things that we might capitalize — for example,
- if we buy a $550 computer, we would not capitalize it. A computer does last more than a year, but a $550 value is not material. It’s important that we be consistent about these practices, so we should not expense a computer we purchase in January and then capitalize and depreciate another computer we purchase in June. If, however, we decided that we were going to replace every computer in the company and make a single $45,000 order from Apple, we would probably have to capitalize and depreciate this over time, since it is a material order for us.
- We have also not capitalized and tracked tool purchase from Home Depot or furniture purchases from ULine. Again, this is a bit of a gray area — it does not make sense for us to track, capitalize, and depreciate every $150 tool we purchase, or $500 desk we buy, but in sum this equipment has value. However, until we update/upgrade our asset tracking and depreciation system, it make sense for us to expense these items, especially since they have been acquired in various intervals over time.
Some Balance Sheet accounts have titles that “sound” right, but are wrong because of their classification as “Balance Sheet” accounts. For example
- The distinction between “maintenance” (An Expense) and “tenant improvements” (an Balance Sheet / Asset) is a bit blurry because we are self-performing many improvements to our spaces. Costs must be material, so it does not make sense to capitalize and depreciate one-off trips to Home Depot to buy bolts and washers as capital expenditures. However, things like safety railings and gates that are affixed to the building should be categorized as Tenant Improvements on the Balance Sheet / Asset accounts.
- Employee Reimbursements Payable is a liability account, not an expense account. It’s used to record the fact that we owe money to somebody, not what we owe them money for. See the Employee Reimbursements Policy for more details.
## Cost of Sales Accounts

### Employees

- Laundry Payroll includes all our Laundry Team Members, Laundry Team Leaders, Shift Managers (everybody hourly) PLUS salaried production managers assigned to a single location.
- Delivery Payroll includes all our drivers and cyclists
- Maintenance Payroll includes all our hourly and salaried maintenance personnel.
- Customer Service and Admin Staff are in the SG&A Payroll, which is an overhead (NOT Cost of Sales) expense.
- Employee Benefits for Production Staff — the pro-rated insurance premiums for any of the staff listed above, net of any payroll deductions made.
### “In Plant” Expenses

- Chemicals and Detergent — this is for laundry chemicals, like detergent, bleach, hydrogen peroxide, and softener that go inside the washing machines. It does not include thermal oil, lubricants, and other chemicals used to maintain or operate machines.
- Utilities —
- Delivery Costs
    - Gas / Tolls / Fines — Self explanatory, although these apply only to the gas / tolls/ fines we use in the vehicles that transport laundry to customers. Any gas related to overhead travel is in the overhead travel category. To be clear, in this context, “gas” refers to Gasoline or Diesel used for vehicles, not natural gas (methane) used to power laundry equipment.
    - Vehicle Leases and Mileage — These are expenses for vehicles we lease or rent and associated usage charges, again only for vehicles that are used to deliver laundry to customers.
- Errors and Refunds to Customers — examples include when we purchase linen on behalf of customers to replace linen they claim we lost or damaged, or when we write a check or use a credit note to do so.
- Intra-Party Subcontractors is when one Wash Cycle Laundry entity bills another for laundry work that it performs on the other’s behalf (e.g., DC does Amtrak but WCL Chelsea LLC bills for it). See the Intra-Party Chart of Accounts For more details.
- Subcontractors for Delivery: Is when we use 3rd parties (like Uber, 3rd party truckers, etc) to move laundry from Point A to Point B).
- Maintenance is for expenses to maintain our plant, equipment, or vehicles. Please see the section on Balance Sheet Accounts (above) for a few examples of what classifies as a maintenance expense versus a Balance sheet account (like equipment, or tenant improvements). Examples of maintenance expenses include:
    - 3rd party repair technicians called
    - Consumable supplies for operation of machines (e.g. guide tape, ironer pads, thermal oil)
    - Small purchases of tools for the maintenance team
- Coin Wash Fees is for cash paid to laundromat owners where our staff do work.
- Rent - Production and Storage is for rent we pay for our production plants and the common area maintenance (CAM) charges that we pay to our landlord. It also includes fees for temporary storage facilities that we use to store production products. It does not include office space, coworking space, or other rent associate with our overhead personnel.
- Utilities (Electric, Gas, Trash, and Water) are the expense we pay for these utilities to provide service to our production locations (think: the water that goes into washing machines, the gas that powers our dryers).
- Wash Costs are miscellaneous plant costs having to do with our laundry operation
    - Employee Food Drinks Perks is for rewards / “thank yous” we buy for our production staff, as well as water, Gatorade, and other snacks/amenities we purchase (especially during the summer). It is NOT for meals during travel.
    - Plastic and Bags is for sealing plastic and bags we use in production.
    - PPE and Uniforms is for uniforms, masks, gloves, aprons, and other supplies we use for our staff to wear during production.
- “SNAFU” is an account that requires a good amount of judgment, sin
### Overhead Expenses

- Accounting fees are those fees charged to us by 3rd parties for accounting services
- Advertising and Marketing: Examples are direct mail, digital ads, etc.
- Bad Debt is customer receivables that we write off.
- Bank Fees is for account maintenance fees, ACH and wire fees, etc.
- Business Taxes and Licenses are for local business taxes and licenses. Examples might include a $300 annual state filing fee, a $75 local license fee. It is NOT for Federal or State income taxes, Sales Tax, or employer withholding taxes.
- Employee Benefits for Admin staff is the pro-rated cost of health insurance and other insurance for Overhead staff.
- HR Consulting and Hiring is for:
    - HR Consultants
    - Background Checks
    - Expenses related to “hiring day” events
    - It is NOT for training expenses (use Training and Professional Development)
- Training and Professional Development is for
    - Expense for 3rd party training / education
    - Sending production staff to training-related conferences or events (I.e., not Gabriel going to an investment-oriented conference, but yes for a Manager going to the Clean Show).
    - Fees for online training tools or classes.
- Insurance is for our business insurance including
    - General Liability
    - Property
    - Worker’s Comp
    - Vehicle Insurance
    - It is NOT for health insurance or employee benefits
- Interest Expense is for interest charged to us by our lenders
- Legal Expenses are for lawyers we pay.
- Merchant Card Services are for the charges made to us to process credit cards.
- Office Expenses are for small office supply purchases, like paper and toner for printers. It is NOT for anything used in the production plant.
- Office Rent is for any office space that is explicitly for our overhead staff. Right now, that’s for co-working spaces. We don’t allocate a % of our plant rent to office rent.
- Payroll Fees is for expenses charged to us by our payroll provider (currently Zenefits ). It is not for payroll taxes charged by the government.
- Payroll SG&A (Sales, General, and Administrative) is for payroll to our administrative / overhead staff. That’s typically everybody on the “KPI Call” except for operations managers (who go in the Laundry Payroll category). I.e., accounting, customer service, HR, executive compensation all goes here.
- Subcontractor 1099 or Upwork is for any overhead “contractor”
- Professional business subscriptions — this is for memberships to professional orgs, like the Association for Linen Management or the Chamber of Commerce
- Telephone and Internet is for cell phones, internet service.
- Travel is for executive / sales / management travel. If people are transporting laundry, it is not travel. Typically, this would be for Gabriel’s travel, travel to conferences, but our quarterly management get-togethers, and other travel not directly related to the delivery of laundry.
- Web Services is for online subscription fees to software.

