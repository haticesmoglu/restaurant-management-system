from PyQt5 import QtCore, QtGui, QtWidgets
from pymongo import MongoClient
from datetime import datetime
import sys, hashlib
import login
import adisyon


class LoginForm(QtWidgets.QWidget): ## LoginForm sınıfı, giriş ekranını oluşturur
    def __init__(self):
        super().__init__() # QWidget'in __init__ fonksiyonunu çağır
        self.setupUi()  #UI elemanlarını kur
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["restaurant_db"] ## Veritabanına bağlan
        self.users_collection = self.db["users"] # "users" koleksiyonuna erişim sağlanır

    def setupUi(self): #setupUi fonksiyonu, UI öğelerini (giriş alanları, butonlar, etiketler vb.) oluşturur.
        self.setObjectName("LoginForm") # Pencere için bir isim belirler
        self.setWindowTitle("Giriş Ekranı")
        self.resize(450, 550) # Pencere boyutları ayarlanır
        self.setFont(QtGui.QFont('', weight=75)) # Pencere fontu ayarlanır

        # Ana widget oluşturulur
        self.widget = QtWidgets.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(30, 20, 370, 480))

        # Arka planda gösterilecek bir etiket (resim)
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(30, 20, 300, 420))
        self.label.setStyleSheet("border-image: url(:/images/istockphoto-494226648-612x612.jpg);\nborder-radius:20px;")

        # Şeffaf bir siyah arka planı olan bir başka etiket
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setGeometry(QtCore.QRect(60, 40, 251, 381))
        self.label_2.setStyleSheet("background-color:rgba(0,0,0,100);\nborder-radius:15px;")

        # "GİRİŞ" başlığı için bir etiket
        self.label_3 = QtWidgets.QLabel("GİRİŞ", self.widget)
        self.label_3.setGeometry(QtCore.QRect(120, 80, 131, 40))
        self.label_3.setFont(QtGui.QFont('', 20, weight=75))
        self.label_3.setStyleSheet("color:rgba(255,255,255,210);")

        # Giriş formunun stil ayarları
        style = """
            background-color:rgba(0,0,0,0);
            border:none;
            border-bottom:2px solid rgba(105,118,132,255);
            color:rgba(255,255,255,230);
            padding-bottom:7px;
        """

        # Kullanıcı adı girişi için QLineEdit oluşturuluyor
        self.kullaniciadi = QtWidgets.QLineEdit(self.widget)
        self.kullaniciadi.setGeometry(QtCore.QRect(90, 130, 200, 40))  # Konum ve boyut
        self.kullaniciadi.setPlaceholderText("KULLANICI ADI") # Placeholder metni
        self.kullaniciadi.setStyleSheet(style) # Stilin uygulanması

        # Şifre girişi için QLineEdit oluşturuluyor
        self.sifre = QtWidgets.QLineEdit(self.widget)
        self.sifre.setGeometry(QtCore.QRect(90, 190, 200, 40))
        self.sifre.setPlaceholderText("ŞİFRE")
        self.sifre.setEchoMode(QtWidgets.QLineEdit.Password) # Şifreyi gizleme
        self.sifre.setStyleSheet(style)

        # Giriş butonu oluşturuluyor
        self.girisbutonu = QtWidgets.QPushButton("Giriş Yap", self.widget)
        self.girisbutonu.setGeometry(QtCore.QRect(90, 250, 200, 40))
        self.girisbutonu.clicked.connect(self.giris) # Butona tıklanınca giris fonksiyonu çalışacak

        # Kayıt ol butonu oluşturuluyor
        self.kayitbutonu = QtWidgets.QPushButton("Kayıt Ol", self.widget)
        self.kayitbutonu.setGeometry(QtCore.QRect(90, 310, 200, 40))
        self.kayitbutonu.clicked.connect(self.kayit) # Butona tıklanınca kayit fonksiyonu çalışacak

    def giris(self):  # Giriş yapma fonksiyonu
        username = self.kullaniciadi.text() # Kullanıcı adı alınır
        password = hashlib.sha256(self.sifre.text().encode()).hexdigest()# Şifre hashlenir

        # Kullanıcı adı ve şifre veritabanında aranır
        if self.users_collection.find_one({"username": username, "password": password}):
            self.hide()  # Başarılı girişte giriş penceresi gizlenir
            self.main_window = RestaurantSystem()  # Ana restoran sistem penceresi başlatılır
            self.main_window.show() # Ana pencere gösterilir
        else:
            # Giriş başarısızsa uyarı mesajı gösterilir
            QtWidgets.QMessageBox.warning(self, "Hata", "Geçersiz kullanıcı adı veya şifre!")

    def kayit(self): # Kayıt olma fonksiyonu
        username = self.kullaniciadi.text() # Kullanıcı adı alınır
        password = self.sifre.text() # Şifre alınır

        # Kullanıcı adı veya şifre boşsa uyarı gösterilir
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")
            return

        # Kullanıcı adı zaten varsa uyarı gösterilir
        if self.users_collection.find_one({"username": username}):
            QtWidgets.QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten mevcut!")
            return

        # Yeni kullanıcı veritabanına eklenir
        self.users_collection.insert_one({
            "username": username,
            "password": hashlib.sha256(password.encode()).hexdigest(),   # Şifre hashlenir
            "created_at": datetime.now()  # Kayıt zamanı
        })
        # Başarı mesajı gösterilir
        QtWidgets.QMessageBox.information(self, "Başarılı", "Kayıt başarıyla oluşturuldu!")


class odemediyalogu(QtWidgets.QDialog): # Ödeme diyalog penceresini oluşturur
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.total = total_amount # Ödenecek toplam miktar
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Ödeme")  # Pencere başlığı
        self.setModal(True) # Modal pencere, yani diğer pencerelerle etkileşime izin vermez
        layout = QtWidgets.QVBoxLayout(self)  # Dikey bir düzen oluşturulur

        # Ödeme türü seçmek için ComboBox
        self.odemeturu = QtWidgets.QComboBox()
        self.odemeturu.addItems(["Nakit", "Kart"])
        self.odemeturu.currentTextChanged.connect(self.on_payment_type_change) # Seçim değiştiğinde fonksiyon çağrılır
        layout.addWidget(self.odemeturu)

        # Nakit ödeme için gerekli alanları içeren widget
        self.cash_widget = QtWidgets.QWidget()
        cash_layout = QtWidgets.QFormLayout(self.cash_widget)

        # Alınan miktar girişi
        self.alinanmiktar = QtWidgets.QLineEdit()
        self.alinanmiktar.setPlaceholderText("Alınan Tutar")
        self.alinanmiktar.textChanged.connect(self.degisimihesapla) # Tutar değiştiğinde ödeme hesaplaması yapılır

        self.change_label = QtWidgets.QLabel("Para Üstü: 0.00 TL")# Para üstü etiketini oluşturur

        # Form düzenine ekler
        cash_layout.addRow("Alınan Tutar:", self.alinanmiktar)
        cash_layout.addRow(self.change_label)

        layout.addWidget(self.cash_widget)

        # Diyalog butonları (onay ve iptal)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)  #Onaylandığında diyaloğu kapat
        buttons.rejected.connect(self.reject)  # İptal edildiğinde diyaloğu kapat
        layout.addWidget(buttons) # Butonları ekler

    def on_payment_type_change(self, payment_type):
        self.cash_widget.setVisible(payment_type == "Nakit")

    def degisimihesapla(self): # Alınan miktar ile toplam tutar arasındaki fark hesaplanır ve gösterilir
        try:
            received = float(self.alinanmiktar.text()) # Alınan miktar
            change = received - self.total
            self.change_label.setText(f"Para Üstü: {change:.2f} TL")  # Para üstü hesaplanıp etiket gösterilir
        except ValueError:
            self.change_label.setText("Para Üstü: 0.00 TL") # Hata durumunda sıfır para üstü gösterilir


class RestaurantSystem(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["restaurant_db"]
        self.orders_collection = self.db["orders"]  # Siparişler koleksiyonu
        self.table_orders = {} # Masaların siparişlerini tutan sözlük

        self.initUI() # UI başlangıç fonksiyonu

    def initUI(self): #Kullanıcı arayüzünü tanımlar ve bileşenleri yerleştirir.
        self.setWindowTitle("Restoran Adisyon Sistemi") # Uygulama penceresinin başlığı
        self.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout(self)  # Ana dikey düzen (layout)

        # Masa düğmeleri
        self.tableLayout = QtWidgets.QGridLayout() # Grid düzeninde masalar için bir yerleşim
        self.tableButtons = {}  # Masa butonlarını tutacak sözlük
        for i in range(1, 11): # 1'den 10'a kadar 10 masa
            btn = QtWidgets.QPushButton(f'MASA {i}')  # Her bir masa için bir buton oluşturuluyor
            btn.clicked.connect(self.secilimasalar) # Butona tıklandığında 'secilimasalar' fonksiyonu çağrılır
            self.tableButtons[f'MASA {i}'] = btn  # Butonlar sözlüğe eklenir
            self.tableLayout.addWidget(btn, (i - 1) // 2, (i - 1) % 2)  # Grid düzenine butonları yerleştir
        layout.addLayout(self.tableLayout) # Masa butonları düzeni ana layout'a eklenir


        # Sipariş tablosu
        self.orderTable = QtWidgets.QTableWidget() # Siparişleri gösterecek tablo
        self.orderTable.setColumnCount(4) # 4 sütun olacak: Ürün, Adet, Birim Fiyat, Toplam
        self.orderTable.setHorizontalHeaderLabels(["ÜRÜN", "ADET", "BİRİM FİYAT", "TOPLAM"])
        layout.addWidget(self.orderTable)  # Sipariş tablosunu ana layout'a ekle

        # Menü butonları
        self.menuLayout = QtWidgets.QGridLayout() # Menü butonları için grid düzeni
        self.prices = { # Menüdeki ürünlerin fiyatları
            "Hamsi Tava": 180, "Kuymak": 250, "Trabzon Pidesi": 100,
            "Akçaabat Köfte": 150, "Lahana Dolma": 120, "Turşu Kavurma": 100,
            "Hamsiköy Sütlacı": 120, "Beton Helva": 80, "Ayran": 10,
            "Çay": 15, "Kola": 30, "Fanta": 30
        }

        row = col = 0 # Grid düzenine başlamak için satır ve sütun sayacı
        for urun, fiyat in self.prices.items(): # Menüdeki her bir ürün ve fiyat için bir buton oluşturuluyor
            btn = QtWidgets.QPushButton(urun)  # Ürün adı ile bir buton oluşturuluyor
            btn.clicked.connect(self.add_order)  # Butona tıklandığında 'add_order' fonksiyonu çalışacak
            self.menuLayout.addWidget(btn, row, col) # Buton grid düzenine ekleniyor
            col += 1 # Sütun sayısını arttır
            if col > 3:  # 4 sütundan fazla olursa bir sonraki satıra geç
                col = 0
                row += 1
        layout.addLayout(self.menuLayout)  # Menü düzenini ana layout'a ekle

        # Alt butonlar
        self.total_label = QtWidgets.QLabel("Toplam: 0 TL") # Toplam tutarı gösterecek etiket
        layout.addWidget(self.total_label) # Toplam etiketini ana layout'a ekle

        self.siparisitemizlebutonu = QtWidgets.QPushButton("Siparişi Temizle")  # Siparişi temizle butonu
        self.siparisitemizlebutonu.clicked.connect(self.siparisitemizle)   # Butona tıklandığında 'siparisitemizle' fonksiyonu çalışır
        layout.addWidget(self.siparisitemizlebutonu) # Butonu layout'a ekle

        self.secilenurunusilbutonu = QtWidgets.QPushButton("Seçili Ürünü Sil") # Seçili ürünü sil butonu
        self.secilenurunusilbutonu.clicked.connect(self.delete_selected_item) # Butona tıklandığında 'secilenurunusil' fonksiyonu çalışır
        layout.addWidget(self.secilenurunusilbutonu)

        self.hesabiodebutonu = QtWidgets.QPushButton("Hesabı Öde")   # Hesabı ödeme butonu
        self.hesabiodebutonu.clicked.connect(self.hesabiode)
        layout.addWidget(self.hesabiodebutonu)

        self.current_table_label = QtWidgets.QLabel("Seçilen Masa: Yok")  # Başlangıçta seçilen masa yok
        layout.addWidget(self.current_table_label)  # Etiketi layout'a ekle

        self.selected_table = None

    def secilimasalar(self):  # Kullanıcı bir masa seçtiğinde çağrılır
        button = self.sender()  # Tıklanan buton alınır
        self.selected_table = button.text() # Seçilen masa ismi alınır
        self.current_table_label.setText(f"Seçilen Masa: {self.selected_table}")  # Etiket güncellenir
        self.display_table_orders() # Seçilen masanın siparişleri gösterilir

    def display_table_orders(self):  # Seçilen masanın siparişlerini tabloya ekler
        self.orderTable.setRowCount(0) # Mevcut satırları sıfırla (temizle)
        if self.selected_table in self.table_orders:   # Eğer masada sipariş varsa
            for item in self.table_orders[self.selected_table]:   # Her sipariş için
                row = self.orderTable.rowCount() # Yeni satır sayısı
                self.orderTable.insertRow(row)  # Yeni satır ekle
                self.orderTable.setItem(row, 0, QtWidgets.QTableWidgetItem(item['name'])) # Ürün ismini ekle
                self.orderTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item['quantity']))) # Adet ekle
                self.orderTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item['price']))) # Birim fiyatı ekle
                self.orderTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item['total']))) # Toplam fiyatı ekle
        self.calculate_total() # Toplam tutarı hesapla

    def add_order(self): # Bir ürün siparişi ekler
        if not self.selected_table: # Eğer masa seçilmemişse
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen önce bir masa seçin!")
            return

        button = self.sender()  # Tıklanan menü butonunu al
        item_name = button.text()  # Ürün ismini al
        price = self.prices[item_name] # Ürün fiyatını al

        if self.selected_table not in self.table_orders:  # Eğer seçilen masada sipariş yoksa
            self.table_orders[self.selected_table] = [] # Yeni bir sipariş listesi oluştur

        for item in self.table_orders[self.selected_table]:  # Mevcut siparişler arasında
            if item['name'] == item_name: # Eğer ürün zaten varsa
                item['quantity'] += 1 # Adedi arttır
                item['total'] = item['quantity'] * item['price']  # Toplam fiyatı güncelle
                self.display_table_orders() # Siparişleri güncelle
                return

        self.table_orders[self.selected_table].append({   # Yeni bir ürün siparişi ekle

            'name': item_name,
            'quantity': 1,
            'price': price,
            'total': price
        })
        self.display_table_orders() # Siparişleri güncelle

    def calculate_total(self):   # Seçilen masanın toplam tutarını hesaplar
        total = sum(item['total'] for item in self.table_orders.get(self.selected_table, [])) # Tüm siparişlerin toplamı
        self.total_label.setText(f"Toplam: {total:.2f} TL") # Toplam tutarı etikete ekle
        return total # Toplam tutarı döndür

    def delete_selected_item(self): # Seçili ürünü siparişlerden siler
        current_row = self.orderTable.currentRow() # Seçili satırı al
        if current_row >= 0: # Eğer geçerli bir satır varsa
            item_name = self.orderTable.item(current_row, 0).text() # Ürün adını al
            self.table_orders[self.selected_table] = [
                item for item in self.table_orders[self.selected_table]
                if item['name'] != item_name # Bu ürünü sil
            ]
            self.display_table_orders()  # Siparişleri güncelle

    def siparisitemizle(self):
        if self.selected_table in self.table_orders: # Eğer seçilen masada sipariş varsa
            self.table_orders[self.selected_table] = []   # Siparişi boşalt
            self.display_table_orders()  # Siparişleri güncelle

    def hesabiode(self):  # Hesap ödemesini yapar
        if not self.selected_table or not self.table_orders.get(self.selected_table):  # Eğer masa seçilmemişse veya sipariş yoksa
            QtWidgets.QMessageBox.warning(self, "Hata", "Ödenecek sipariş bulunamadı!")
            return

        total = self.calculate_total()  # Toplam tutarı hesapla

        dialog = odemediyalogu(total, self) # Ödeme diyaloğu oluştur
        if dialog.exec_() == QtWidgets.QDialog.Accepted:  #Eğer ödeme kabul edilirse
            payment_type = dialog.odemeturu.currentText()   # Ödeme türünü al

            self.orders_collection.insert_one({ # Ödeme bilgisini veritabanına kaydet
                "table": self.selected_table,
                "items": self.table_orders[self.selected_table],
                "total": total,
                "payment_type": payment_type,
                "date": datetime.now()
            })

            self.table_orders[self.selected_table] = [] # Masadaki siparişi sıfırla
            self.display_table_orders() # Siparişleri güncelle
            QtWidgets.QMessageBox.information(self, "Başarılı", "Ödeme tamamlandı!")  # Başarı mesajı göster


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login = LoginForm()
    login.show()
    sys.exit(app.exec_())