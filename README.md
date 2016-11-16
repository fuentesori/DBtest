# Personal Stock Portfolio

Group Members:
Oriana Fuentes oif2102
Harry Munroe jhm2152

Introduction:
The Personal Stock Portfolio Application allows a user to manage their stock
portfolios and bank accounts to effectively track and edit their stock
positions.

Functions of the portfolio:
Users may either create an account or log in using an existing account. once in
their account, they may modify their profile details, add or modify their bank
account information, move money between bank accounts and their portfolios,
or buy and sell stocks. They may also delete their portfolios, delete bank
accounts or delete their accounts entirely.

## Navigating the Application:
### Login:
The user arrives at the login page, where they may either log in or create a new
account for themselves. They must enter their first and last name, email, street
address, phone number, SSN, and create a password. Upon account creation, the
user will receive their user id so they can log in again in the future.
### Portfolio:
A logged in user gets redirected to the portfolios page where they may view
their portfolios, add new portfolios or bank accounts, perform stock
transactions and finance their portfolios using their bank accounts.
### Profile:
From the Portfolio page user may navigate to their profile to edit their
information or bank account information, or delete their accounts. They may also
click logout to leave the application and clear their data so another user is
unable to see their information.

## Restrictions:
### Login:
Users must enter a valid portfolio id number, using only numerical input.
If they do not enter a valid id number they will be redirected to a page letting
them know their id was invalid that redirects back to the login page. The login
must also match up to the correct password given in the database. The password
must only contain numbers, letters and underscores.
### Add User:
Each field has restrictions to ensure a clean database and to prevent sql
injection on the front end (it is also rejected in the application itself. The
restrictions are as follows:
first and last name: must only contain letters
* Email: must be formatted as an email with the appropriate characters, @ symbol
appropriately placed, et cetera
* Address: must be formatted as an address with only alphanumeric characters plus
white space, commas and dashes
* Phone: only numbers, dashes and parentheses, formatted as shown on the page
* ssn: only numbers and dashes, formatted as shown on the page
* password: only alphanumeric characters and underscores
* Portfolio:
The user may select portfolios from the drop down menu. They may add bank
accounts, restricting ABA numbers to 8 numerical digits and Account numbers to
10 numerical digits. Users may transfer funds between their bank accounts and
portfolios and buy stocks with the money in their portfolios, as long as the
funds in the portfolio do not go below 0.
### Profile:
Users may update their profiles with new information if they choose (all formats
are the same as in the Add User section). They may also add more bank accounts
in this section. Users may delete their accounts as long as at least one bank
account is set with direct deposit so that the application will return the money
once the user deletes their account.
