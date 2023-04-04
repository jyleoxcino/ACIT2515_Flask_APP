# ACIT-2515 - Flask API App

## About

Grocery Manager Application created using Python and PyQt5 GUI library.

This application connects to an Flask API endpoint to get data from a database created from SQL Alchemy and the Flask-SQLAlchemy extension.

![[grocery_manager_example.png]]

![[order_manager_exmaple.png]]
## Installation

Clone this repository

```
$ git clone https://github.com/jyleoxcino/ACIT2515_Flask_APP.git
```

## Usage

### Dependencies

This application requires Python 3.11 and some other modules.

Install dependencies using `pip`

`pip install flask flask-alchemy PyQt5`

### Setup

1. Create and populate database from repo directory.

`$ python.exe .\create_tables.py || .\create_products.py || .\create_order.py`

2. Start Flask development webserver.

`$ python.exe .\webserver.py`

3. Start Flask_APP

`$ python.exe .\GroceryManager.py`


