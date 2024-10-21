from PyQt5.QtWidgets import QMainWindow, QMessageBox,QLineEdit,QLabel, QPushButton
from PyQt5 import uic,QtWidgets, QtCore, QtGui
from resources import resources
from dotenv import load_dotenv
import requests
import sys
import os

load_dotenv()

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi('resources/ui/main.ui', self)
        self.close_app = self.findChild(QPushButton,"close")
        self.mini = self.findChild(QPushButton,"minimiz")
        self.maxwin = self.findChild(QPushButton, "maxwin")
        self.search = self.findChild(QLineEdit,"search")
        self.temp = self.findChild(QLabel, "temp")
        self.wind = self.findChild(QLabel, "wind")
        self.uv = self.findChild(QLabel, "uv")
        self.city_display = self.findChild(QLabel, "city_display")
        self.time_icon = self.findChild(QLabel, "time_icon")
        self.time_display = self.findChild(QLabel, "time_display")
        self.search.returnPressed.connect(self.get_weather)
        self.mini.clicked.connect(self.minimiz_application)
        self.close_app.clicked.connect(self.close_application)
        self.maxwin.clicked.connect(self.full_screen)

        #transparent and frameless window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.temp.hide()
        self.wind.hide()
        self.uv.hide()
        self.time_display.hide()

        self.full_screen_mod = False

        # Variables for dragging
        self.dragging = False
        self.startPos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.startPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.startPos)
            event.accept()

    def get_weather(self):
        city = self.search.text()
        if city:
            key = os.getenv("WeatherKey")
            api_key = f"{key}"  # Replace with your WeatherAPI API key
            url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"

            try:
                response = requests.get(url)
                data = response.json()

                if "error" not in data:

                    time_period = None
                    self.city_display.setText(f"City: {city}")
                    time_stamp = data['location']['localtime'].split(" ")[1]
                    print("Time",time_stamp)
                    self.time_display.setText(f"Time: {time_stamp}")
                    hour, minute = map(int, time_stamp.split(":"))

                    #Determining time period
                    if 0 <= hour < 12:
                        time_period = "Morning"
                    elif 12 <= hour < 18:
                        time_period = "Day"
                    else:
                        time_period = "Night"

                    self.temp.setText(str(data['current']['temp_c']))
                    self.wind.setText(str(data['current']['wind_kph']) + " Kmh")
                    #humidity = data['current']['humidity']
                    self.uv.setText(str(data['current']['uv']))
                    self.temp.show()
                    self.wind.show()
                    self.uv.show()
                    self.time_display.show()

                    if time_period == "Night":
                        self.time_icon.setPixmap(QtGui.QPixmap(":/icons/icons/night.png"))
                    elif time_period == "Day":
                        self.time_icon.setPixmap(QtGui.QPixmap(":/icons/icons/sun.png"))
                    else:
                        self.time_icon.setPixmap(QtGui.QPixmap(":/icons/icons/sunrise.png"))

                else:
                    self.wind.setText("City not found. Please try again.")
                    self.temp.hide()
                    self.uv.hide()
                    self.wind.show()
            except Exception as e:
                self.wind.setText(f"Error: {str(e)}")
                self.temp.hide()
                self.uv.hide()
                self.wind.show()
        else:
            self.wind.setText("Please enter a city name.")
            self.temp.hide()
            self.uv.hide()
            self.wind.show()

    def close_application(self):

        QtWidgets.QApplication.quit()

    def minimiz_application(self):

        self.showMinimized()

    def full_screen(self):

        if not self.full_screen_mod:
            self.showFullScreen()
            self.full_screen_mod = True
        else:
            self.showNormal()
            self.full_screen_mod = False

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
