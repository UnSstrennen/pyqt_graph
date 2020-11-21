import sys
import sqlite3
import datetime

from PyQt5 import uic
from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QColorDialog

conn = sqlite3.connect("data.db") # подключаемся к базе
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS action
                      (_id INTEGER PRIMARY KEY AUTOINCREMENT, color_RGB TEXT, action_type TEXT, da_te TEXT)
                   """) # создаю таблицу


class BrushPoint:  # кисть
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color # цвет

    def draw(self, painter):
        r = self.color[0] # составляющие цвета
        g = self.color[1]
        b = self.color[2]
        painter.setBrush(QBrush(QColor(r, g, b)))
        painter.setPen(QColor(r, g, b))
        painter.drawEllipse(self.x - 5, self.y - 5, 10, 10)


class Line:  # линия
    def __init__(self, sx, sy, ex, ey, color):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.color = color

    def draw(self, painter):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        painter.setBrush(QBrush(QColor(r, g, b)))
        painter.setPen(QColor(r, g, b))
        painter.drawLine(self.sx, self.sy, self.ex, self.ey)


class Circle:  # окружность
    def __init__(self, cx, cy, x, y, color):
        self.cx = cx
        self.cy = cy
        self.x = x
        self.y = y
        self.color = color

    def draw(self, painter):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        painter.setBrush(QBrush(QColor(r, g, b, 0)))  # заливка прозрачная (последний 0)
        painter.setPen(QColor(r, g, b))
        radius = int(((self.cx - self.x) ** 2 + (self.cy - self.y) ** 2) ** 0.5)
        painter.drawEllipse(self.cx - radius, self.cy - radius, 2 * radius, 2 * radius)


class Canvas(QWidget):  # панели для рисования
    def __init__(self):
        super(Canvas, self).__init__()

        self.objects = []  # объекты, которые уже нарисованы
        self.instrument = 'brush'  # инструмент, который используется, по умолчания кисть
        self.color = (0, 0, 0, 255) # цвет рисования

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        for obj in self.objects:
            obj.draw(painter)
        painter.end()

    def mousePressEvent(self, event):
        if self.instrument == 'brush':
            self.objects.append(BrushPoint(event.x(), event.y(), self.color))
            self.update()
        elif self.instrument == 'line':
            self.objects.append((Line(event.x(), event.y(), event.x(), event.y(), self.color)))
            self.update()
        elif self.instrument == 'circle':
            self.objects.append(Circle(event.x(), event.y(), event.x(), event.y(), self.color))
            self.update()
        now = datetime.datetime.now() # текущее время
        cursor.execute("""INSERT INTO action (color_RGB, action_type, da_te)
                                      VALUES (?, ?, ?)""", (str(self.color[:3]), self.instrument, now.strftime("%d-%m-%Y %H:%M:%S"))
                       ) # создаю новую запись в таблице
        conn.commit()

    def mouseMoveEvent(self, event):
        if self.instrument == 'brush':
            self.objects.append(BrushPoint(event.x(), event.y(), self.color))
            self.update()
        elif self.instrument == 'line':
            self.objects[-1].ex = event.x()
            self.objects[-1].ey = event.y()
            self.update()
        elif self.instrument == 'circle':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()

    def setBrush(self):
        self.instrument = 'brush'

    def setLine(self):
        self.instrument = 'line'

    def setCircle(self):
        self.instrument = 'circle'

    def showDialog(self): # выбор цвета
        col = QColorDialog.getColor()
        if col.isValid():
            self.color = col.getRgb()


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('window.ui', self)

        self.setCentralWidget(Canvas())

        self.action_color.triggered.connect(self.centralWidget().showDialog)
        self.action_brush.triggered.connect(self.centralWidget().setBrush)
        self.action_line.triggered.connect(self.centralWidget().setLine)
        self.action_circle.triggered.connect(self.centralWidget().setCircle)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.show()
    sys.exit(app.exec())
