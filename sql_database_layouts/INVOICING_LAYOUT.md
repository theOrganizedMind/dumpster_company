# Dumpster Company Invoicing SQL Database Layout: 

This document describes the columns, types, and possible values for a dumpster
company SQL database.

---

## Invoicing SQL Database Layout

| Column Name      | Type                | Example Values / Notes                                                                 |
|------------------|---------------------|----------------------------------------------------------------------------------------|
| **InvoiceNumber**| TEXT                | 1005                                           
| **Company**      | VARCHAR(255)        | Company Name                                        
| **Street**       | VARCHAR(100)        | Example (123 Lewis Way)                                                            
| **City**         | VARCHAR(80)         | Example (Jacksonville)                               
| **State**        | VARCHAR(10)         | Example (FL)
| **Country**      | VARCHAR(10)         | Example (USA)
| **Date**         | DATE                | YYYY-MM-DD
| **Driver**       | VARCHAR(45)         | Driver Name
| **Size**         | VARCHAR(20)         | Dumpster Size (Example: 30 yard)
| **Type**         | VARCHAR(20)         | Type of material (Example: Recycling, Clean-Fill, C&D)
| **Description**  | VARCHAR(45)         | Description (Example: Initial Drop, Swap, Dump & Remove)
| **SiteContact**  | VARCHAR(45)         | Site Contact Name (Example: John Doe)
| **Phone**        | VARCHAR(20)         | Phone Number (Example: 1234569567)
| **Disposal**     | VARCHAR(80)         | Disposal Location (Example: Music City)
| **Tons**         | FLOAT               | Tonnage
| **DisposalCost** | FLOAT               | Disposal Price
| **Price**        | FLOAT               | Invoice Amount
| **GrossProfit**  | FLOAT               | Formula (Price - DisposalCost)

---

## Notes
