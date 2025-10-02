import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from pymongo import MongoClient
from datetime import datetime

class Ui_MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        #MongoDB'ye bağlama
        self.client = MongoClient("mongodb://localhost:27017/")  # Change the URI if you're using MongoDB Atlas
        self.db = self.client["restaurant_db"]  # Database ismi
        self.orders_collection = self.db["orders"]  # Siparişler için

        self.setWindowTitle("Restoran Adisyon Sistemi")
        self.setGeometry(100, 100, 800, 600)

        self.orderTable = []  # Siparişleri tutacak liste
        self.prices = {
            "Hamsi Tava": 180,
            "Kuymak": 250,
            "Trabzon Pidesi": 100,
            "Akçaabat Köfte": 150,
            "Lahana Dolma": 120,
            "Turşu Kavurma": 100,
            "Hamsiköy Sütlacı": 120,
            "Beton Helva": 80,
            "Ayran": 10,
            "Çay": 15,
            "Kola": 30,
            "Fanta": 30
        }

        self.initUI() #Bu, sınıfın bir metodu ve UI'yi başlatan fonksiyondur.

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self) #arayüzdeki ana düzen

        # Masa seçimi
        self.tableLayout = QtWidgets.QGridLayout()
        self.tableButtons = {}
        for i in range(1, 11):  # 10 masamız var
            button = QtWidgets.QPushButton(f'MASA {i}')
            button.clicked.connect(self.select_table)
            self.tableButtons[f'MASA {i}'] = button
            self.tableLayout.addWidget(button, (i - 1) // 2, (i - 1) % 2)

        layout.addLayout(self.tableLayout)

        # Siparişler
        self.orderTableWidget = QtWidgets.QTableWidget(self)
        self.orderTableWidget.setColumnCount(4)
        self.orderTableWidget.setHorizontalHeaderLabels(["ÜRÜN", "ADET", "BİRİM FİYAT", "TOPLAM"])
        layout.addWidget(self.orderTableWidget)

        # Menü
        self.menuLayout = QtWidgets.QGridLayout()
        self.menuButtons = {}
        row = 0
        col = 0
        for yemekadi, price in self.prices.items():
            button = QtWidgets.QPushButton(yemekadi) #QPushButton(yemekadi) ile her bir yemek öğesi için bir buton oluşturuluyor
            button.clicked.connect(self.siparisekle) #Bu metod, tıklanan öğeyi sipariş listesine eklemeyi sağlar.
            self.menuButtons[yemekadi] = button
            self.menuLayout.addWidget(button, row, col)
            col += 1
            if col > 3:  #Her yeni buton eklendikçe col (sütun) bir artırılır.
                col = 0
                row += 1

        layout.addLayout(self.menuLayout)

        # Toplam tutar
        self.toplamtutar = QtWidgets.QLabel("Toplam Tutar: 0", self)
        layout.addWidget(self.toplamtutar)

        # Sipariş temizleme ve hesaplama butonları
        self.siparisitemizle = QtWidgets.QPushButton("Siparişi Temizle", self)
        self.siparisitemizle.clicked.connect(self.clear_order)
        layout.addWidget(self.siparisitemizle)

        self.siparisihesapla = QtWidgets.QPushButton("Hesapla", self)
        self.siparisihesapla.clicked.connect(self.toplamhesapla)
        layout.addWidget(self.siparisihesapla)

        # Hesabı ödeme butonu
        self.hesabiode = QtWidgets.QPushButton("Hesabı Öde", self)
        self.hesabiode.clicked.connect(self.pay_bill)
        layout.addWidget(self.hesabiode)

        self.currentTableLabel = QtWidgets.QLabel("Seçilen Masa: Yok ", self)
        layout.addWidget(self.currentTableLabel)

        self.selectedTable = None

    def select_table(self):
        button = self.sender()
        self.selectedTable = button.text()
        self.currentTableLabel.setText(f"Seçilen Masa: {self.selectedTable}")
        self.orderTableWidget.setRowCount(0)  # Siparişi temizle

    def siparisekle(self):
        if not self.selectedTable:
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen önce bir masa seçin!")
            return

        button = self.sender()
        item_name = button.text()
        price = self.prices[item_name]

        # Sipariş edilen ürün zaten var mı kontrol et
        row_count = self.orderTableWidget.rowCount()
        for row in range(row_count):
            if self.orderTableWidget.item(row, 0).text() == item_name:
                current_quantity = int(self.orderTableWidget.item(row, 1).text())
                self.orderTableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(current_quantity + 1)))
                self.orderTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(price * (current_quantity + 1))))
                self.toplamhesapla()
                return

        # Yeni ürün ekle
        row_position = self.orderTableWidget.rowCount()
        self.orderTableWidget.insertRow(row_position)
        self.orderTableWidget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(item_name))
        self.orderTableWidget.setItem(row_position, 1, QtWidgets.QTableWidgetItem("1"))
        self.orderTableWidget.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(price)))
        self.orderTableWidget.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(price)))

        self.toplamhesapla()

    def toplamhesapla(self):
        total = 0
        row_count = self.orderTableWidget.rowCount()
        for row in range(row_count):
            quantity = int(self.orderTableWidget.item(row, 1).text())
            unit_price = float(self.orderTableWidget.item(row, 2).text())
            total += quantity * unit_price
        self.toplamtutar.setText(f"Toplam Tutar: {total:.2f}")

    def clear_order(self):
        self.orderTableWidget.setRowCount(0)
        self.toplamhesapla()

    def pay_bill(self):
        total = 0
        row_count = self.orderTableWidget.rowCount()
        for row in range(row_count):
            quantity = int(self.orderTableWidget.item(row, 1).text())
            unit_price = float(self.orderTableWidget.item(row, 2).text())
            total += quantity * unit_price

        #Fatura tutarını görüntüle ve onay iste
        confirmation = QtWidgets.QMessageBox.question(self, "Hesap",
                                                      f"Toplam tutar: {total:.2f} TL. Ödemek ister misiniz?",
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if confirmation == QtWidgets.QMessageBox.Yes:
            QtWidgets.QMessageBox.information(self, "Ödeme", "Ödeme başarılı. Teşekkürler!")

            # Save order to MongoDB
            order_data = {
                "table": self.selectedTable,
                "items": [],
                "total": total,
                "date": datetime.now()
            }

            for row in range(self.orderTableWidget.rowCount()):
                item_name = self.orderTableWidget.item(row, 0).text()
                quantity = int(self.orderTableWidget.item(row, 1).text())
                unit_price = float(self.orderTableWidget.item(row, 2).text())
                order_data["items"].append({
                    "item": item_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total": quantity * unit_price
                })

            # Sipariş verilerini MongoDB'ye ekle
            self.orders_collection.insert_one(order_data)

            self.clear_order()  # Ödemeden sonra siparişi temizle
        else:
            QtWidgets.QMessageBox.information(self, "Ödeme İptali", "Ödeme iptal edildi.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())

