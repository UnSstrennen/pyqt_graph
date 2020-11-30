import sys
import sqlite3
import datetime
import math

from PyQt5 import uic
from PyQt5.QtGui import QBrush, QColor, QPainter, QImage, QPen
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QColorDialog, QDialog, QFrame

conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS action
                      (_id INTEGER PRIMARY KEY AUTOINCREMENT, color_RGB TEXT, action_type TEXT, da_te TEXT)
                   """)


class BrushPoint:  # кисть
    def __init__(self, x, y, color, wid):
        self.x = x
        self.y = y
        self.color = color
        self.diam = wid

    def draw(self, painter):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        painter.setBrush(QBrush(QColor(r, g, b)))
        painter.setPen(QColor(r, g, b))
        painter.drawEllipse(self.x - 5, self.y - 5, self.diam, self.diam)


class Line:  # линия
    def __init__(self, sx, sy, ex, ey, color, thick):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.color = color
        self.thick = thick

    def draw(self, painter):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        painter.setBrush(QBrush(QColor(r, g, b)))
        painter.setPen(QPen(QColor(r, g, b), self.thick))
        painter.drawLine(self.sx, self.sy, self.ex, self.ey)


class Circle:  # окружность
    def __init__(self, cx, cy, x, y, color, fill, thick):
        self.cx = cx
        self.cy = cy
        self.x = x
        self.y = y
        self.color = color
        self.color_fill = (fill[0], fill[1], fill[2], fill[3])
        self.thick = thick

    def draw(self, painter):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        r1 = self.color_fill[0]
        g1 = self.color_fill[1]
        b1 = self.color_fill[2]
        a1 = self.color_fill[3]
        painter.setBrush(QBrush(QColor(r1, g1, b1, a1)))
        painter.setPen(QPen(QColor(r, g, b), self.thick))
        radius = int(((self.cx - self.x) ** 2 + (self.cy - self.y) ** 2) ** 0.5)
        painter.drawEllipse(self.cx - radius, self.cy - radius, 2 * radius, 2 * radius)


class Rectangle:  # Прямоугольник
    def __init__(self, cx, cy, x, y, color, fill, thick):
        self.cx = cx
        self.cy = cy
        self.x = x
        self.y = y
        self.color = color
        self.color_fill = (fill[0], fill[1], fill[2], fill[3])
        self.thick = thick

    def draw(self, painter):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        r1 = self.color_fill[0]
        g1 = self.color_fill[1]
        b1 = self.color_fill[2]
        a1 = self.color_fill[3]
        painter.setBrush(QBrush(QColor(r1, g1, b1, a1)))
        painter.setPen(QPen(QColor(r, g, b), self.thick))
        painter.drawRect(self.cx, self.cy, self.x - self.cx, self.y - self.cy)


class Square:  # Квадрат
    def __init__(self, cx, cy, x, y, color, fill, thick):
        self.cx = cx
        self.cy = cy
        self.x = x
        self.y = y
        self.color = color
        self.color_fill = (fill[0], fill[1], fill[2], fill[3])
        self.thick = thick

    def draw(self, painter):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        r1 = self.color_fill[0]
        g1 = self.color_fill[1]
        b1 = self.color_fill[2]
        a1 = self.color_fill[3]
        painter.setBrush(QBrush(QColor(r1, g1, b1, a1)))
        painter.setPen(QPen(QColor(r, g, b), self.thick))
        radius = int(((self.cx - self.x) ** 2 + (self.cy - self.y) ** 2) ** 0.5)
        painter.drawRect(self.cx - radius, self.cy - radius, 2 * radius, 2 * radius)


class Star:
    def __init__(self, angle, outerRadius, innerRadius, color):
        self.angle, self.outerRadius, self.innerRadius = angle, outerRadius, innerRadius
        self.color = color
        self.path = None

    def draw(self, painter):
        r = self.color[0]
        g = self.color[1]
        b = self.color[2]
        self.path = QPainterPath()
        angle = 2 * math.pi / self.angle
        self.path.moveTo(self.outerRadius, 0)
        for step in range(1, self.angle + 1):
            self.path.lineTo(
                self.innerRadius * math.cos((step - 0.5) * angle),
                self.innerRadius * math.sin((step - 0.5) * angle)
            )
            self.path.lineTo(
                self.outerRadius * math.cos(step * angle),
                self.outerRadius * math.sin(step * angle)
            )
        self.path.closeSubpath()
        painter.setBrush(QBrush(QColor(r, g, b, 0)))
        painter.setPen(QColor(r, g, b))
        painter.drawPath(self.path)


class Canvas(QWidget):  # панели для рисования
    def __init__(self):
        super(Canvas, self).__init__()

        self.objects = []  # объекты, которые уже нарисованы
        self.instrument = 'brush'  # инструмент, который используется, по умолчания кисть
        self.fill_color = [0, 0, 0, 0]
        self.color = (0, 0, 0, 255)
        self.thick = 5

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        for obj in self.objects:
            obj.draw(painter)
        painter.end()

    def mousePressEvent(self, event):
        if self.instrument == 'brush':
            self.objects.append(BrushPoint(event.x(), event.y(), self.color, self.thick))
            self.update()
        elif self.instrument == 'line':
            self.objects.append((Line(event.x(), event.y(), event.x(), event.y(), self.color, self.thick)))
            self.update()
        elif self.instrument == 'circle':
            self.objects.append(Circle(event.x(), event.y(), event.x(), event.y(), self.color, self.fill_color,
                                       self.thick))
            self.update()
        elif self.instrument == 'eraser':
            self.objects.append(BrushPoint(event.x(), event.y(), (240, 240, 240, 0), self.thick))
            self.update()
        elif self.instrument == 'rect':
            self.objects.append(Rectangle(event.x(), event.y(), event.x(), event.y(), self.color, self.fill_color,
                                          self.thick))
            self.update()
        elif self.instrument == 'square':
            self.objects.append(Square(event.x(), event.y(), event.x(), event.y(), self.color, self.fill_color,
                                       self.thick))
            self.update()
        # elif self.instrument == 'star':
        #    self.objects.append(Star())
        now = datetime.datetime.now()
        cursor.execute("""INSERT INTO action (color_RGB, action_type, da_te)
                                      VALUES (?, ?, ?)""", (str(self.color[:3]), self.instrument,
                                                            now.strftime("%d-%m-%Y %H:%M:%S"))
                       )
        conn.commit()

    def mouseMoveEvent(self, event):
        if self.instrument == 'brush':
            self.objects.append(BrushPoint(event.x(), event.y(), self.color, self.thick))
            self.update()
        elif self.instrument == 'line':
            self.objects[-1].ex = event.x()
            self.objects[-1].ey = event.y()
            self.update()
        elif self.instrument == 'circle':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()
        elif self.instrument == 'eraser':
            self.objects.append(BrushPoint(event.x(), event.y(), (240, 240, 240, 0), self.thick))
            self.update()
        elif self.instrument == 'rect':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()
        elif self.instrument == 'square':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()


class ThickDialog(QDialog):
    def __init__(self, parent=None, obj=None):
        super().__init__(parent)
        uic.loadUi('DialogThick.ui', self)
        self.initUI()
        self.thikness = obj.thick
        self.canvas = obj

        self.slider.setMinimum(1)
        self.slider.setValue(self.thikness)
        self.slider.valueChanged.connect(self.thick)

    def initUI(self):
        self.okay.clicked.connect(self.getThick)
        self.cancel.clicked.connect(self.closeEvent)

    def closeEvent(self, event):
        self.close()

    def getThick(self):
        self.canvas.thick = self.thikness
        self.close()

    def thick(self, value=10):
        self.thikness = value


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('window.ui', self)

        self.setCentralWidget(Canvas())

        self.action_color.triggered.connect(self.showColorDialog)
        self.action_brush.triggered.connect(self.setBrush)
        self.action_line.triggered.connect(self.setLine)
        self.action_circle.triggered.connect(self.setCircle)
        self.action_thick.triggered.connect(self.setThick)
        self.action_erase_ever.triggered.connect(self.del_all)
        self.action_eraser.triggered.connect(self.setEraser)
        self.action_rect.triggered.connect(self.setRect)
        self.action_square.triggered.connect(self.setSquare)
        self.action_color_fill.triggered.connect(self.showColorDialogFill)
        self.action_fill.triggered.connect(self.setFill)

        self.fill_flag = False

    def setBrush(self):
        self.centralWidget().instrument = 'brush'

    def setLine(self):
        self.centralWidget().instrument = 'line'

    def setCircle(self):
        self.centralWidget().instrument = 'circle'

    def showColorDialog(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.centralWidget().color = col.getRgb()

    def showColorDialogFill(self):
        col = QColorDialog.getColor()
        if col.isValid():
            h = col.getRgb()
            self.centralWidget().fill_color[0] = h[0]
            self.centralWidget().fill_color[1] = h[1]
            self.centralWidget().fill_color[2] = h[2]

    def setFill(self):
        if not self.fill_flag:
            self.fill_flag = True
            self.centralWidget().fill_color[3] = 255
        else:
            self.fill_flag = False
            self.centralWidget().fill_color[3] = 0

    def setThick(self):
        dlg = ThickDialog(self, self.centralWidget())
        dlg.exec()

    def setEraser(self):
        self.centralWidget().instrument = 'eraser'

    def setRect(self):
        self.centralWidget().instrument = 'rect'

    def setSquare(self):
        self.centralWidget().instrument = 'square'

    def del_all(self):
        self.centralWidget().objects = []
        self.centralWidget().update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.show()
    sys.exit(app.exec())

