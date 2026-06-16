# Fund Agent Ledger DB Architecture

Below file outlines the architecture of the Fund Agent Ledger database.

## Investors
Investor_ID as Int Autoincrement Primary Key
Fund as Str
Commitment as Float
Contributions as Float
Distributions as Float
Recallable_Distributions as Float

## Investments
Investment_ID as Int Autoincrement Primary Key
Deal_Name as Str
Commitment as Float
Contributions as Float
Distributions as Float
Recallable_Distributions as Float

## General Ledger
Batch_ID as Int Autoincremnt Primary Key
Deal_Name as Str Foreign Key
Account_Code as Str Foreign Key
Debit as Float
Credit as Float
Description as Str
Date_GL as Datetime
Date_Change as Datetime

Not fully fleshed out yet, still requires a transaction table to accompany the general ledger table

## Accounts
Account_Code as Str Primary Key
Type as Str
Name as Str
Natural_State as Str


