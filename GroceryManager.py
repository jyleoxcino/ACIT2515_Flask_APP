import sys
import requests
import json
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, Qt

########################################
#
#               GROCERY MANAGER
#
########################################


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        loadUi("GroceryManager.ui", self)

        self.connect_to_api()

        self.exitAction.triggered.connect(self.close)
        self.connectAction.triggered.connect(self.connect_to_api)

        productTable_header = self.productTable.horizontalHeader()
        productTable_header.setSectionResizeMode(0, QHeaderView.Stretch)
        productTable_header.setSectionResizeMode(1, QHeaderView.Stretch)
        productTable_header.setSectionResizeMode(2, QHeaderView.Stretch)

        orderTable_vheader = self.orderTable.verticalHeader()
        orderTable_vheader.setVisible(False)
        orderTable_header = self.orderTable.horizontalHeader()
        orderTable_header.setSectionResizeMode(0, QHeaderView.Fixed)
        orderTable_header.resizeSection(0, 200)
        orderTable_header.setSectionResizeMode(1, QHeaderView.Stretch)
        orderTable_header.setSectionResizeMode(2, QHeaderView.Stretch)
        orderTable_header.setSectionResizeMode(3, QHeaderView.Stretch)
        orderTable_header.setSectionResizeMode(4, QHeaderView.Stretch)
        orderTable_header.setSectionResizeMode(5, QHeaderView.Stretch)

        self.productsButton.clicked.connect(self.productView)
        self.ordersButton.clicked.connect(self.orderView)
        self.createProduct.clicked.connect(self.create_product)
        self.modifyProduct.clicked.connect(self.modify_product)
        self.deleteProduct.clicked.connect(self.delete_product)
        self.searchProduct.clicked.connect(self.search_table)

        self.createOrder.clicked.connect(self.create_order)
        self.modifyOrder.clicked.connect(self.modify_order)
        self.processOrder.clicked.connect(self.process_order)
        self.viewOrder.clicked.connect(self.view_order)
        self.deleteOrder.clicked.connect(self.delete_order)
        self.productTable.doubleClicked.connect(self.modify_product)
        self.orderTable.doubleClicked.connect(self.double_click_order)
        self.searchOrder.clicked.connect(self.search_table)

        self.ordersRadio.clicked.connect(self.populate_tables)
        self.oosRadio.clicked.connect(self.populate_tables)
        self.productsRadio.clicked.connect(self.populate_tables)
        self.pendingRadio.clicked.connect(self.populate_tables)
        self.processedRadio.clicked.connect(self.populate_tables)

        self.buttonRefresh.clicked.connect(self.reload_api)

    #########################
    #       Functions       #
    #########################

    def set_defaults(self):
            self.view.setCurrentIndex(0)
            self.productsButton.setDisabled(True)
            self.ordersButton.setDisabled(False)
            self.ordersRadio.setChecked(True)
            self.populate_tables()

    def productView(self):
        self.view.setCurrentIndex(0)
        self.productsButton.setDisabled(True)
        self.ordersButton.setDisabled(False)
        self.productsRadio.setChecked(False)
        self.ordersRadio.setChecked(True)
        self.populate_tables()

    def orderView(self):
        self.view.setCurrentIndex(1)
        self.productsButton.setDisabled(False)
        self.ordersButton.setDisabled(True)
        self.ordersRadio.setChecked(False)
        self.productsRadio.setChecked(True)
        self.populate_tables()

    def selected_product(self):
        _data = {
            "name": self.productTable.selectedItems()[0].text(),
            "price": str(self.productTable.selectedItems()[1].text()),
            "quantity": str(self.productTable.selectedItems()[2].text())
        }
        return _data

    def selected_order(self):
        _id = int(self.orderTable.selectedItems()[0].text())
        _data = self.api_controller.get_order(id=_id)
        return _data

    def create_product(self):
        _create = ProductManager(flag=0, products=self.api_controller.products)
        _create.signal.connect(self.api_controller.create_product)
        _create.exec_()
        self.reload_api()
        self.populate_tables()

    def modify_product(self):
        if len(self.productTable.selectedItems()) > 0:
            _modify = ProductManager(flag=1, data=self.selected_product())
            _modify.signal.connect(self.api_controller.modify_product)
            _modify.exec_()
        else:
            return ErrorManager(message="Please select a Product").exec_()
        self.reload_api()
        self.populate_tables()

    def delete_product(self):
        if len(self.productTable.selectedItems()) > 0:
            _delete = ProductManager(flag=2, data=self.selected_product())
            _delete.signal.connect(self.api_controller.delete_product)
            _delete.exec_()
        else:
            return ErrorManager(message="Please select a Product").exec_()
        self.reload_api()
        self.populate_tables()

    def double_click_order(self):
        _status = self.orderTable.selectedItems()[4].text()
        if len(self.orderTable.selectedItems()) > 0:
            if _status == "False":
                self.modify_order()
            else:
                self.view_order()

    def create_order(self):
        _create = OrderManager(flag=0, products=self.api_controller.products)
        _create.signal.connect(self.api_controller.create_order)
        _create.exec_()
        self.reload_api()
        self.populate_tables()

    def modify_order(self):
        if len(self.orderTable.selectedItems()) > 0:
            _status = self.orderTable.selectedItems()[4].text()
            _id = self.orderTable.selectedItems()[0].text()
            if _status == "False":
                _modify = OrderManager(
                    flag=1, products=self.api_controller.products, data=self.selected_order(), id=_id)
                _modify.signal.connect(self.api_controller.modify_order)
                _modify.exec_()
            else:
                return ErrorManager(message="This order has already been processed and can no longer be modified.").exec_()
        else:
            return ErrorManager(message='Please select an order.').exec_()

    def process_order(self):
        if len(self.orderTable.selectedItems()) > 0:
            _status = self.orderTable.selectedItems()[4].text()
            _id = self.orderTable.selectedItems()[0].text()
            if _status == "False":
                _process = OrderManager(
                    flag=2, products=self.api_controller.products, data=self.selected_order(), id=_id)
                _process.signal.connect(self.api_controller.process_order)
                _process.exec_()
            else:
                return ErrorManager(message="This order has already been processed.").exec_()
        else:
            return ErrorManager(message='Please select an order.').exec_()
        self.reload_api()
        self.populate_tables

    def view_order(self):
        if len(self.orderTable.selectedItems()) > 0:
            _id = self.orderTable.selectedItems()[0].text()
            try:
                _view = OrderManager(
                    flag=3, products=self.api_controller.products, data=self.selected_order(), id=_id)
                _view.exec_()
            except:
                ErrorManager(message="An error has ocurred.").exec_()
        else:
            return ErrorManager(message='Please select an order.').exec_()

    def delete_order(self):
        if len(self.orderTable.selectedItems()) > 0:
            _id = self.orderTable.selectedItems()[0].text()
            _process = OrderManager(
                flag=4, products=self.api_controller.products, data=self.selected_order(), id=_id)
            _process.signal.connect(self.api_controller.delete_order)
            _process.exec_()
        else:
            return ErrorManager(message="Please select an order").exec_()
        self.reload_api()
        self.populate_tables

    def connect_to_api(self):
        _hook = API_Controller()
        if _hook.connection == True:
            self.api_controller = API_Controller()
            self.centralwidget.setDisabled(False)
            self.set_defaults()
        else:
            self.centralwidget.setDisabled(True)

    def reload_api(self):
        self.api_controller.reload()
        self.populate_tables()

    def get_keyword(self):
        _index = self.view.currentIndex()
        _search = SearchWindow(index=_index)
        _search.exec_()
        try:
            _data = _search.get_data()
        except:
            return
        return _data

    def search_table(self):
        _data = self.get_keyword()
        try:
            _keyword = _data['keyword']
            _flag = _data['flag']
        except:
            return
        row = 0
        if _flag == 0:
            self.productTable.clearContents()
            self.productTable.setRowCount(0)
            for product in self.api_controller.products:
                if str.__contains__(product['name'], _keyword):
                    self.productTable.insertRow(row)
                    self.productTable.setItem(
                        row, 0, QtWidgets.QTableWidgetItem(product['name']))
                    self.productTable.setItem(
                        row, 1, QtWidgets.QTableWidgetItem(str(product['price'])))
                    self.productTable.setItem(
                        row, 2, QtWidgets.QTableWidgetItem(str(product['quantity'])))
                    row += 1
        else:
            self.orderTable.clearContents()
            self.orderTable.setRowCount(0)
            if _flag == 1:
                for order in self.api_controller.orders:
                    if str.__contains__(order['name'], _keyword):
                        self.orderTable.insertRow(row)
                        self.orderTable.setItem(
                            row, 0, QtWidgets.QTableWidgetItem(str(order['id'])))
                        self.orderTable.setItem(
                            row, 1, QtWidgets.QTableWidgetItem(order['name']))
                        self.orderTable.setItem(
                            row, 2, QtWidgets.QTableWidgetItem(order['address']))
                        self.orderTable.setItem(
                            row, 3, QtWidgets.QTableWidgetItem(str(order['date_created'])))
                        self.orderTable.setItem(
                            row, 4, QtWidgets.QTableWidgetItem(str(order['completed'])))
                        if order['date_processed'] == None:
                            self.orderTable.setItem(
                                row, 5, QtWidgets.QTableWidgetItem(""))
                        else:
                            self.orderTable.setItem(
                                row, 5, QtWidgets.QTableWidgetItem(str(order['date_processed'])))
                        row += 1
            else:
                for order in self.api_controller.orders:
                    if str.__contains__(order['address'], _keyword):
                        self.orderTable.insertRow(row)
                        self.orderTable.setItem(
                            row, 0, QtWidgets.QTableWidgetItem(str(order['id'])))
                        self.orderTable.setItem(
                            row, 1, QtWidgets.QTableWidgetItem(order['name']))
                        self.orderTable.setItem(
                            row, 2, QtWidgets.QTableWidgetItem(order['address']))
                        self.orderTable.setItem(
                            row, 3, QtWidgets.QTableWidgetItem(str(order['date_created'])))
                        self.orderTable.setItem(
                            row, 4, QtWidgets.QTableWidgetItem(str(order['completed'])))
                        if order['date_processed'] == None:
                            self.orderTable.setItem(
                                row, 5, QtWidgets.QTableWidgetItem(""))
                        else:
                            self.orderTable.setItem(
                                row, 5, QtWidgets.QTableWidgetItem(str(order['date_processed'])))
                        row += 1

    def populate_tables(self):
        if self.view.currentIndex() == 0: # Show All
            self.productTable.clearContents()
            self.productTable.setRowCount(0)
            row = 0
            if self.ordersRadio.isChecked():
                self.productTable.setRowCount(len(self.api_controller.products))
                for product in self.api_controller.products:
                    self.productTable.setItem(
                        row, 0, QtWidgets.QTableWidgetItem(product['name']))
                    self.productTable.setItem(
                        row, 1, QtWidgets.QTableWidgetItem(str(product['price'])))
                    self.productTable.setItem(
                        row, 2, QtWidgets.QTableWidgetItem(str(product['quantity'])))
                    row += 1
            elif self.oosRadio.isChecked():
                for product in self.api_controller.products:
                    if product['quantity'] == 0:
                        self.productTable.insertRow(row)
                        self.productTable.setItem(
                            row, 0, QtWidgets.QTableWidgetItem(product['name']))
                        self.productTable.setItem(
                            row, 1, QtWidgets.QTableWidgetItem(str(product['price'])))
                        self.productTable.setItem(
                            row, 2, QtWidgets.QTableWidgetItem(str(product['quantity'])))
                        row += 1
        else:
            self.orderTable.clearContents()
            self.orderTable.setRowCount(0)
            row = 0
            if self.productsRadio.isChecked(): # Filter by OOS
                self.orderTable.setRowCount(len(self.api_controller.orders))
                for order in self.api_controller.orders:
                    self.orderTable.setItem(
                        row, 0, QtWidgets.QTableWidgetItem(str(order['id'])))
                    self.orderTable.setItem(
                        row, 1, QtWidgets.QTableWidgetItem(order['name']))
                    self.orderTable.setItem(
                        row, 2, QtWidgets.QTableWidgetItem(order['address']))
                    self.orderTable.setItem(
                        row, 3, QtWidgets.QTableWidgetItem(str(order['date_created'])))
                    self.orderTable.setItem(
                        row, 4, QtWidgets.QTableWidgetItem(str(order['completed'])))
                    if order['date_processed'] == None:
                        self.orderTable.setItem(
                            row, 5, QtWidgets.QTableWidgetItem(""))
                    else:
                        self.orderTable.setItem(
                            row, 5, QtWidgets.QTableWidgetItem(str(order['date_processed'])))
                    row += 1
            elif self.pendingRadio.isChecked(): # Filter by Pending
                for order in self.api_controller.orders:
                    if order['completed'] == False:
                        self.orderTable.insertRow(row)
                        self.orderTable.setItem(
                            row, 0, QtWidgets.QTableWidgetItem(str(order['id'])))
                        self.orderTable.setItem(
                            row, 1, QtWidgets.QTableWidgetItem(order['name']))
                        self.orderTable.setItem(
                            row, 2, QtWidgets.QTableWidgetItem(order['address']))
                        self.orderTable.setItem(
                            row, 3, QtWidgets.QTableWidgetItem(str(order['date_created'])))
                        self.orderTable.setItem(
                            row, 4, QtWidgets.QTableWidgetItem(str(order['completed'])))
                        if order['date_processed'] == None:
                            self.orderTable.setItem(
                                row, 5, QtWidgets.QTableWidgetItem(""))
                        else:
                            self.orderTable.setItem(
                                row, 5, QtWidgets.QTableWidgetItem(str(order['date_processed'])))
                        row += 1
            elif self.processedRadio.isChecked(): # Filter by Processed
                for order in self.api_controller.orders:
                    if order['completed'] == True:
                        self.orderTable.insertRow(row)
                        self.orderTable.setItem(
                            row, 0, QtWidgets.QTableWidgetItem(str(order['id'])))
                        self.orderTable.setItem(
                            row, 1, QtWidgets.QTableWidgetItem(order['name']))
                        self.orderTable.setItem(
                            row, 2, QtWidgets.QTableWidgetItem(order['address']))
                        self.orderTable.setItem(
                            row, 3, QtWidgets.QTableWidgetItem(str(order['date_created'])))
                        self.orderTable.setItem(
                            row, 4, QtWidgets.QTableWidgetItem(str(order['completed'])))
                        if order['date_processed'] == None:
                            self.orderTable.setItem(
                                row, 5, QtWidgets.QTableWidgetItem(""))
                        else:
                            self.orderTable.setItem(
                                row, 5, QtWidgets.QTableWidgetItem(str(order['date_processed'])))
                        row += 1



########################################
#
#               PRODUCT MANAGER
#
########################################
class ProductManager(QDialog):
    signal = pyqtSignal(object)

    def __init__(self, parent=None, flag=None, data=None, products=None):
        super().__init__(parent)
        loadUi("ProductManager.ui", self)

        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowContextHelpButtonHint)
        self.cancelButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.accept)
        self.deleteButton.clicked.connect(self.delete)

        self.products_list = []

        if flag is None:
            self.flag = None
        else:
            self.flag = flag

        if products is None:
            self.products = None
        else:
            self.products = products
            for product in self.products:
                self.products_list.append(product['name'])

        if data is None:
            self.data = None
        else:
            self.data = data
            self.nameTextbox.setDisabled(True)
            self.nameTextbox.setText(self.data['name'])
            self.priceTextbox.setText(str(self.data['price']))
            self.quantityTextbox.setText(str(self.data['quantity']))

        # 0 - Create
        # 1 - Modify
        # 2 - Delete

        if flag == 0:
            self.flagLabel.setText("Create Product")
            self.view.setCurrentIndex(0)
            self.create
        elif flag == 1:
            self.flagLabel.setText("Modify Product")
            self.view.setCurrentIndex(0)
        elif flag == 2:
            self.flagLabel.setText("Delete Product")
            self.view.setCurrentIndex(1)
            self.priceTextbox.setDisabled(True)
            self.quantityTextbox.setDisabled(True)

    def accept(self):
        try:
            _name = self.nameTextbox.text().lower()
            if not _name:
                raise TypeError
            for product in self.products_list:
                if _name == product:
                    return ErrorManager(f"{_name} already exists in the database.").exec_()
        except TypeError:
            ErrorManager("Invalid Input, Product Name cant be empty.").exec_()
            return
        try:
            _price = float(self.priceTextbox.text())
        except ValueError:
            ErrorManager(
                'Invalid Input, Price must be a positive decimal value.').exec_()
            return
        try:
            _quantity = int(self.quantityTextbox.text())
            if _quantity < 0:
                raise ValueError
        except ValueError:
            ErrorManager(
                'Invalid Input, Quantity must be a positive float value.').exec_()
            return
        self.signal.emit(
            {"name": _name, "price": _price, "quantity": _quantity})
        super().accept()

    def delete(self):
        _name = self.data['name']
        self.signal.emit(_name)
        super().accept()

########################################
#
#               ORDER MANAGER
#
########################################


class OrderManager(QDialog):

    signal = pyqtSignal(object)

    def __init__(self, parent=None, products=None, id=None, data=None, flag=None):
        super().__init__(parent)
        loadUi("OrderManager.ui", self)

        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowContextHelpButtonHint)
        self.cancelButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.accept)
        self.addProductButton.clicked.connect(self.add_product)
        self.deleteProductButton.clicked.connect(self.delete_product)
        self.processButton.clicked.connect(self.process)
        self.deleteButton.clicked.connect(self.process)
        productTable_header = self.productTable.horizontalHeader()
        productTable_header.setSectionResizeMode(0, QHeaderView.Stretch)
        productTable_header.setSectionResizeMode(1, QHeaderView.Stretch)
        productTable_header.setSectionResizeMode(2, QHeaderView.Stretch)

        if products is None:
            self.products = None
        else:
            self.products = products

        if id is None:
            self.id = None
        else:
            self.id = id

        if data is None:
            self.data = None
        else:
            self.data = data
            self.nameTextbox.setText(self.data['customer_name'])
            self.addressTextbox.setText(self.data['customer_address'])
            self.dateTextbox.setText(self.data['date_created'])
            self.processedTextbox.setText(self.data['date_processed'])
            self.orderTextbox.setText(str(self.id))
            self.costTextbox.setText(str(round(self.data['price'], 2)))
            self.nameTextbox.setReadOnly(True)
            self.addressTextbox.setReadOnly(True)

        if flag is None:
            self.flag = False
        else:
            self.flag = flag

        # 0 Create
        # 1 Modify
        # 2 Process
        # 3 View
        # 4 Delete

        if self.flag == 0:
            self.dateTextbox.setText(self.get_date())
            self.view.setCurrentIndex(0)
            self.flagLabel.setText("Create Order")
            self.orderTextbox.setDisabled(True)
            self.productTable.setRowCount(0)
            self.costTextbox.setText("0.00")
        elif self.flag == 1:
            self.view.setCurrentIndex(0)
            self.flagLabel.setText("Modify Order")
        elif self.flag == 2:
            self.view.setCurrentIndex(1)
            self.flagLabel.setText("Process Order")
            self.addProductButton.setDisabled(True)
            self.deleteProductButton.setDisabled(True)
        elif self.flag == 3:
            self.flagLabel.setText("View Order")
            self.view.setCurrentIndex(0)
            self.addProductButton.setDisabled(True)
            self.deleteProductButton.setDisabled(True)
        elif self.flag == 4:
            self.flagLabel.setText("Delete Order")
            self.view.setCurrentIndex(2)
            self.productTable.setDisabled(True)
            self.addProductButton.setDisabled(True)
            self.deleteProductButton.setDisabled(True)

        if flag != 0:
            self.populate_tables()
            self.get_products()

    def get_products(self):
        _order_list = []
        for row in range(self.productTable.rowCount()):
            _itemName = self.productTable.item(row, 0)
            _itemQuantity = self.productTable.item(row, 1)
            if _itemName is not None and _itemQuantity is not None:
                _name = _itemName.text()
                _quantity = _itemQuantity.text()
                _order_list.append({"name": _name, "quantity": int(_quantity)})
        return _order_list

    def get_date(self):
        _current_date = datetime.now()
        _formatted_date = _current_date.strftime("%Y-%m-%d %H:%M:%S")
        return _formatted_date

    def check_stock(self, name, quantity):
        _quantity = quantity
        for product in self.products:
            if product['name'] == name:
                if int(product['quantity']) < int(quantity):
                    ErrorManager(
                        'Entered quantity is greater than store quantity.\nOrder quantity set to store quantity.').exec_()
                    _quantity = str(product['quantity'])
        return _quantity

    def calculate_price(self, name, quantity):
        _local_price = 0
        for product in self.products:
            if product['name'] == name:
                _local_price = (product['price']) * quantity
        return _local_price

    def populate_tables(self):
        self.productTable.setRowCount(len(self.data['products']))
        row = 0
        for product in self.data['products']:
            _name = product['name']
            _quantity = int(product['quantity'])
            _price = self.calculate_price(_name, _quantity)
            _formatted_price = str("{:.2f}".format(_price))
            self.productTable.setItem(
                row, 0, QtWidgets.QTableWidgetItem(_name))
            self.productTable.setItem(
                row, 1, QtWidgets.QTableWidgetItem(str(_quantity)))
            self.productTable.setItem(
                row, 2, QtWidgets.QTableWidgetItem(_formatted_price))
            row += 1

    def add_product(self):
        _add_product = ProductOrderManager(products=self.products)
        _add_product.exec_()
        try:
            _data = _add_product.get_data()
        except:
            return
        try:
            _name = _data['name']
        except TypeError:
            return
        for row in range(self.productTable.rowCount()):
            tableItem = self.productTable.item(row, 0)
            if tableItem.text() == _name:
                return ErrorManager('Product is already in order.').exec_()
        _quantity = self.check_stock(_name, _data['quantity'])
        _price = self.calculate_price(_name, int(_quantity))
        _new_cost = float(self.costTextbox.text()) + _price
        self.costTextbox.setText(str("{:.2f}".format(_new_cost)))
        if _data is not None:
            _products = self.productTable.rowCount()
            self.productTable.setRowCount(_products + 1)
            _this_product = _products
            self.productTable.setItem(
                _this_product, 0, QtWidgets.QTableWidgetItem(_name))
            self.productTable.setItem(
                _this_product, 1, QtWidgets.QTableWidgetItem(str(_quantity)))
            self.productTable.setItem(
                _this_product, 2, QtWidgets.QTableWidgetItem(str("{:.2f}".format(_price))))
            self.populate_tables

    def accept(self):
        _price = self.costTextbox.text()
        _float_price = round(float(_price), 2)
        try:
            _name = self.nameTextbox.text()
            if not _name:
                raise TypeError
        except TypeError:
            ErrorManager("Customer name can't be empty.").exec_()
            return
        try:
            _address = self.addressTextbox.text()
        except ValueError:
            ErrorManager("Address can't be empty").exec_()
            return
        if self.flag == 1:
            self.signal.emit({"id": self.id, "payload": {"customer_name": _name,
                             "customer_address": _address, "products": self.get_products(), "price": _float_price}})
        else:
            self.signal.emit({"customer_name": _name, "customer_address": _address,
                             "products": self.get_products(), "price": _float_price})
        super().accept()

    def delete_product(self):
        if len(self.productTable.selectedItems()) > 0:
            _selected_row = self.productTable.currentRow()
            _price = float(self.productTable.item(_selected_row, 2).text())
            _new_cost = float(self.costTextbox.text()) - _price
            self.costTextbox.setText(str("{:.2f}".format(_new_cost)))
            self.productTable.removeRow(_selected_row)
        else:
            return ErrorManager(message="Please select a Product").exec_()

    def process(self):
        if self.flag == 3:
            self.reject()
        else:
            _id = self.id
            self.signal.emit(_id)
            super().accept()


class ProductOrderManager(QDialog):
    def __init__(self, parent=None, products=None):
        super().__init__(parent)
        loadUi("ProductOrderManager.ui", self)

        self.data = None
        self.products_names = []

        if products is None:
            self.products = None
        else:
            self.products = products
            self.productComboBox.addItem('')
            for product in self.products:
                self.products_names.append(product['name'])
                self.productComboBox.addItem(product['name'])

        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowContextHelpButtonHint)
        self.addButton.clicked.connect(self.add_product)
        self.cancelButton.clicked.connect(self.reject)
        self.quantityTextbox.setText('0')
        self.quantityTextbox.returnPressed.connect(
            self.quantityTextbox.clearFocus)
        self.quantityTextbox.editingFinished.connect(self.calculate_price)

    def get_data(self):
        return self.data

    def calculate_price(self):
        _name = self.productComboBox.currentText()
        try:
            _quantity = int(self.quantityTextbox.text())
        except ValueError:
            return
        _local_price = 0
        for product in self.products:
            if product['name'] == _name:
                _local_price = (product['price']) * _quantity
        self.priceTextbox.setText(str("{:.2f}".format(_local_price)))

    def add_product(self):
        _name = self.productComboBox.currentText()
        if _name not in self.products_names:
            return ErrorManager('This is not a valid product.').exec_()
        _price = self.priceTextbox.text()
        _quantity = self.quantityTextbox.text()
        try:
            _quantity = int(_quantity)
            if _quantity <= 0:
                raise ValueError
        except ValueError:
            return ErrorManager('Quantity must be a positive whole number.').exec_()
        self.data = {"name": _name, "price": _price, "quantity": _quantity}
        super().accept()


########################################
#
#               Error Manager
#
########################################
class ErrorManager(QDialog):
    def __init__(self, message=None, parent=None):
        super().__init__(parent)
        loadUi("ErrorManager.ui", self)

        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowContextHelpButtonHint)

        if message is None:
            self.errorMessage.setText("Error")
        else:
            self.errorMessage.setText(message)

        self.exitButton.clicked.connect(self.reject)

########################################
#
#               Error Manager
#
########################################
class SearchWindow(QDialog):

    signal = pyqtSignal(bool)

    def __init__(self, parent=None, index=None):
        super().__init__(parent)
        loadUi("SearchWindow.ui", self)

        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowContextHelpButtonHint)

        if index is None:
            self.index = None
        else:
            self.index = index

        if self.index == 0:
            self.view.setCurrentIndex(0)
            self.productRadio.setChecked(True)
        else:
            self.view.setCurrentIndex(1)
            self.nameRadio.setChecked(True)

        self.cancelButton.clicked.connect(self.reject)
        self.searchButton.clicked.connect(self.accept)

    def get_data(self):
        return self.data

    def get_flag(self):
        if self.productRadio.isChecked():
            _flag = 0
        elif self.nameRadio.isChecked():
            _flag = 1
        else:
            _flag = 2
        return _flag

    def accept(self):
        _flag = self.get_flag()
        self.data = {"keyword": self.keywordTextbox.text(), "flag": _flag}
        super().accept()


########################################
#
#               API CONTROLLER
#
########################################
class API_Controller():
    def __init__(self):

        self.connection = False
        self.url = 'http://127.0.0.1:5000/api/'

        try:
            self.products = requests.get(
                'http://127.0.0.1:5000/api/product/', headers={'Accept': 'application/json'}).json()
            self.orders = requests.get(
                'http://127.0.0.1:5000/api/order/', headers={'Accept': 'application/json'}).json()
            self.order_products = requests.get(
                'http://127.0.0.1:5000/api/order_products/', headers={'Accept': 'application/json'}).json()
            self.connection = True
        except requests.exceptions.HTTPError as error:
            ErrorManager(
                message=f"Can't connect to API endpoint.\n Is the server running?").exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(
                message="Can't connect to API endpoint.\n Is the server running?").exec_()

    def create_product(self, data=None):
        _data = data
        _name = data['name']
        try:
            _create = requests.post(
                url='http://127.0.0.1:5000/api/product/', json=_data)
            _create.raise_for_status()
            ErrorManager(
                message=f"Success\n{_name} added to the database.").exec_()
        except requests.exceptions.HTTPError as error:
            ErrorManager(message=f'{error}').exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(message=f'{error}').exec_()

    def modify_product(self, data):
        _data = data
        _name = data['name']
        try:
            _create = requests.put(
                url=f'http://127.0.0.1:5000/api/product/{_name}', json=_data)
            _create.raise_for_status()
            ErrorManager(message=f"{_name} has been modified.").exec_()
        except requests.exceptions.HTTPError as error:
            ErrorManager(message=f'{error}').exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(message=f'{error}').exec_()

    def delete_product(self, name):
        _name = name
        try:
            _create = requests.delete(
                url=f'http://127.0.0.1:5000/api/product/{_name}')
            _create.raise_for_status()
            ErrorManager(
                message=f"{_name} has been deleted from the database.").exec_()
        except requests.exceptions.HTTPError as error:
            ErrorManager(message=f'{error}').exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(message=f'{error}').exec_()

    def get_order(self, id):
        _id = id
        try:
            _get = requests.get(
                url=f'http://127.0.0.1:5000/api/order/{_id}', headers={'Accept': 'application/json'})
            _get.raise_for_status()
            return _get.json()
        except requests.exceptions.HTTPError as error:
            ErrorManager(message=f'{error}').exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(message=f'{error}').exec_()

    def create_order(self, data):
        _json = data
        try:
            _get = requests.post(url=f'http://127.0.0.1:5000/api/order/',
                                 headers={'Accept': 'application/json'}, json=_json)
            _get.raise_for_status()
            ErrorManager(message=f"Order has been created.").exec_()
        except requests.exceptions.HTTPError as error:
            ErrorManager(message=f'{error}').exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(message=f'{error}').exec_()

    def modify_order(self, data):
        _json = data['payload']
        _id = data['id']
        try:
            _modify = requests.put(url=f'http://127.0.0.1:5000/api/order/{_id}', headers={
                                   'Accept': 'application/json'}, json=_json)
            _modify.raise_for_status()
            ErrorManager(message=f"Order {_id} has been modified.").exec_()
        except requests.exceptions.HTTPError as error:
            ErrorManager(message=f'{error}').exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(message=f'{error}').exec_()

    def process_order(self, id):
        _id = id
        try:
            _process = requests.post(
                url=f'http://127.0.0.1:5000/api/order/{_id}')
            _process.raise_for_status()
            ErrorManager(message=f"Order {_id} has been processed.").exec_()
        except requests.exceptions.HTTPError as error:
            ErrorManager(message=f'{error}').exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(message=f'{error}').exec_()

    def delete_order(self, id):
        _id = id
        try:
            _process = requests.delete(
                url=f'http://127.0.0.1:5000/api/order/{_id}')
            _process.raise_for_status()
            ErrorManager(message=f"Order {_id} has been deleted.").exec_()
        except requests.exceptions.HTTPError as error:
            ErrorManager(message=f'{error}').exec_()
        except requests.exceptions.RequestException as error:
            ErrorManager(message=f'{error}').exec_()

    def reload(self):
        self.products = requests.get(
            'http://127.0.0.1:5000/api/product/', headers={'Accept': 'application/json'}).json()
        self.orders = requests.get(
            'http://127.0.0.1:5000/api/order/', headers={'Accept': 'application/json'}).json()
        self.order_products = requests.get(
            'http://127.0.0.1:5000/api/order_products/', headers={'Accept': 'application/json'}).json()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    app.exec_()
