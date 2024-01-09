from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
import webbrowser
import requests
import aiohttp
import asyncio
import pytz

last_msg = ''
token = ''
base_url = 'https://db27569b-6fc0-4837-a84e-c9ec867c0f0c-00-3ajve1sx4f01d.sisko.replit.dev/'


# Checking new messages by constant requests:
# the IDs received in the last request == id saved in last_msg

# Проверка новых сообщений постоянными запросами:
# идентификатор, полученный в последнем запросе == идентификатор сохраненый в last_msg
class NewMsgCheck(QtCore.QObject):
    new_message = QtCore.pyqtSignal(str)

    def run(self):
        asyncio.run(self.newmsg_check())

    async def newmsg_check(self):
        global last_msg
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{base_url}take?token={token}') as response:
                    result = await response.json()
                    if list(result.keys())[0] != last_msg and result[list(result.keys())[0]] != '':
                        last_msg = list(result.keys())[0]
                        msg = result[list(result.keys())[0]]
                        try:
                            msgtime_utc = datetime.strptime(msg.split(' ')[0].strip('[]'),
                                                            '%H:%M').replace(tzinfo=pytz.utc)
                            local_tz = datetime.now().astimezone().tzinfo
                            msgtime_local = msgtime_utc.astimezone(local_tz).strftime('%H:%M')
                            msg = msg.split(' ')
                            msg[0] = f'[{msgtime_local}]'
                            self.new_message.emit(' '.join(msg))
                        except ValueError:
                            self.new_message.emit(msg)


# Input with sending via enter \ Ввод с отправкой через Enter
class EnterHandler(QtWidgets.QTextEdit):
    def __init__(self, main_win, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.main_win = main_win

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
            try:
                self.main_win.send_message()
            except Exception as e:
                print(e)
        else:
            super(EnterHandler, self).keyPressEvent(event)


def gitopen():
    webbrowser.open('https://github.com/Nimotrosik/peretirach')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.about_action = QtWidgets.QAction(self)
        self.about_window = AboutWindow()
        self.github_action = QtWidgets.QAction(self)
        response = requests.get(f'{base_url}take_name')
        self.byte_array = QtCore.QByteArray(response.content)
        self.pixmap = QtGui.QPixmap()
        self.logo = QtWidgets.QLabel(self)
        self.WriteTokenText = QtWidgets.QLabel(self)
        self.TokenLine = QtWidgets.QTextEdit(self)
        self.CreateChat = QtWidgets.QPushButton(self)
        self.CreateChat.setGeometry(QtCore.QRect(10, 440, 921, 61))
        self.GoToTheChat = QtWidgets.QPushButton(self)

        self.leave = QtWidgets.QPushButton(self)
        self.entertext = EnterHandler(self, self)
        self.nicktext = QtWidgets.QLabel(self)
        self.sendbtn = QtWidgets.QPushButton(self)
        self.nickname = QtWidgets.QTextEdit(self)
        self.msges = QtWidgets.QTextEdit(self)

        self.NewMsgCheck = NewMsgCheck()
        self.thread = QtCore.QThread()

    def setup_ui(self):
        self.setFixedSize(940, 580)
        self.setWindowTitle('Перетира.ч')

        self.about_action.setText('О программе')
        self.about_action.triggered.connect(self.about)
        self.menuBar().addAction(self.about_action)
        self.github_action.setText('GitHub')
        self.github_action.triggered.connect(gitopen)
        self.menuBar().addAction(self.github_action)

        # Token input interface \ Интерфейс ввода токена
        self.pixmap.loadFromData(self.byte_array)
        self.logo.setPixmap(self.pixmap)
        self.logo.setScaledContents(True)
        pixmap_width = self.pixmap.width()
        pixmap_height = self.pixmap.height()
        x_position = (self.width() - pixmap_width) // 2
        self.logo.setGeometry(x_position, 35, pixmap_width, pixmap_height)

        self.WriteTokenText.setGeometry(QtCore.QRect(0, 210, 941, 81))
        font = QtGui.QFont()
        font.setFamily('Open Sans')
        font.setPointSize(14)
        font.setWeight(75)
        self.WriteTokenText.setFont(font)
        self.WriteTokenText.setAlignment(QtCore.Qt.AlignCenter)
        self.WriteTokenText.setObjectName('WriteTokenText')

        self.TokenLine.setGeometry(QtCore.QRect(290, 285, 371, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setFamily('Open Sans SemiBold')
        self.TokenLine.setFont(font)
        self.TokenLine.setObjectName('TokenLine')
        self.TokenLine.setAlignment(QtCore.Qt.AlignCenter)

        font = QtGui.QFont()
        font.setFamily('Open Sans Semibold')
        font.setBold(False)
        font.setWeight(50)
        self.CreateChat.setFont(font)
        self.CreateChat.setObjectName('CreateChat')

        self.GoToTheChat.setGeometry(QtCore.QRect(10, 510, 921, 61))
        font = QtGui.QFont()
        font.setFamily('Open Sans Semibold')
        font.setBold(False)
        font.setWeight(50)
        self.GoToTheChat.setFont(font)
        self.GoToTheChat.setObjectName('GoToTheChat')

        # Chat interface \ Интерфейс чата
        self.leave.setGeometry(QtCore.QRect(20, 35, 151, 41))
        self.leave.setObjectName('leave')
        self.leave.hide()

        self.entertext.setGeometry(QtCore.QRect(20, 500, 641, 61))
        self.entertext.setAutoFormatting(QtWidgets.QTextEdit.AutoNone)
        self.entertext.setObjectName('entertext')
        self.entertext.hide()

        self.nicktext.setGeometry(QtCore.QRect(570, 35, 61, 41))
        self.nicktext.setObjectName('label')
        self.nicktext.hide()

        self.sendbtn.setGeometry(QtCore.QRect(680, 500, 231, 61))
        self.sendbtn.setObjectName('sendbtn')
        self.sendbtn.hide()

        self.nickname.setGeometry(QtCore.QRect(640, 45, 271, 20))
        self.nickname.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.nickname.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.nickname.setObjectName('nickname')
        self.nickname.setPlainText('Аноним')
        self.nickname.hide()

        self.msges.setGeometry(QtCore.QRect(20, 85, 891, 400))
        self.msges.setAutoFormatting(QtWidgets.QTextEdit.AutoNone)
        self.msges.setReadOnly(True)
        self.msges.setStyleSheet('QTextEdit { background-color: white; color: black; }')
        self.msges.setText('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        self.msges.setObjectName('msges')
        self.msges.hide()

        self.setup_btns()
        self.NewMsgCheck.moveToThread(self.thread)
        self.thread.started.connect(self.NewMsgCheck.run)
        self.NewMsgCheck.new_message.connect(self.update_messages)
        self.thread.start()

        QtCore.QMetaObject.connectSlotsByName(self)

    # The function which sets button labels and apply click handlers
    # Функция, которая устанавливает метки кнопок и применяет обработчики кликов
    def setup_btns(self):
        self.GoToTheChat.setText('Войти в чат')
        self.GoToTheChat.clicked.connect(self.join_chat)
        self.WriteTokenText.setText('Введите токен чата')
        self.CreateChat.setText('Создать чат')
        self.CreateChat.clicked.connect(self.create_chat)

        self.leave.setText('Покинуть чат')
        self.leave.clicked.connect(self.leave_chat)
        self.nicktext.setText('Твой ник')
        self.sendbtn.setText('Отправить')
        self.sendbtn.clicked.connect(self.send_message)

    # Function for connecting to chats \ Функция подключения к чатам
    def join_chat(self):
        global token
        global last_msg
        if '\n' not in self.TokenLine.toPlainText():
            # Check is chat already exists, if it doesn't - creates it
            # Проверить, существует ли чат, если нет — создать его
            if requests.get(f'{base_url}/check_chat?token={self.TokenLine.toPlainText()}').text == 'Чат создан':
                msges = requests.get(f'{base_url}/take_all?token={self.TokenLine.toPlainText()}').json()
                last_msg = msges[1]
                token = self.TokenLine.toPlainText()
                for i in range(len(msges[0])):
                    try:
                        msgtime_utc = datetime.strptime(msges[0][i].split(' ')[0].strip('[]'),
                                                        '%H:%M').replace(tzinfo=pytz.utc)
                        local_tz = datetime.now().astimezone().tzinfo
                        msgtime_local = msgtime_utc.astimezone(local_tz).strftime('%H:%M')
                        msges[0][i] = msges[0][i].split(' ')
                        msges[0][i][0] = f'[{msgtime_local}]'
                        msges[0][i] = ' '.join(msges[0][i])
                    except ValueError:
                        pass
                # If there are fewer than 22 messages in a chat, blank lines are added to the beginning
                # to appear messages to the bottom

                # Если в чате менее 22 сообщений, в начало добавляются пустые строки
                # чтобы сообщения появлялись внизу
                if len(msges[0]) <= 22:
                    msges[0].insert(0, '\n' * (22 - len(msges[0])))
                self.TokenLine.setText('')
                self.msges.setText('\n'.join(msges[0]) + '\n')
                self.hide_connecting_ui()
            else:
                QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Чата с таким токеном не существует,'
                                                               ' но теперь он создан и вы можете в него войти',
                                               QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Некорректный токен', QtWidgets.QMessageBox.Ok)

    # Function for creating chats \ Функция для создания чатов
    def create_chat(self):
        global token
        # Check token valid (token must be a string without line breaks)
        # Проверка корректности токена (в токене не должно быть переноса строк)
        if '\n' not in self.TokenLine.toPlainText():
            if requests.get(f'{base_url}/create_chat?token={self.TokenLine.toPlainText()}').text == 'Чат создан':
                token = self.TokenLine.toPlainText()
                self.TokenLine.setText('')
                self.msges.setText('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
                self.hide_connecting_ui()
            else:
                QtWidgets.QMessageBox.critical(self, 'Ошибка',
                                               'Чат с таким токеном существует', QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Некорректный токен', QtWidgets.QMessageBox.Ok)

    # The UI for joining a chat is hidden, the chat UI appears
    # Интерфейс входа в чат скрыт, интерфейс чата становится видимым
    def hide_connecting_ui(self):
        self.logo.hide()
        self.GoToTheChat.hide()
        self.WriteTokenText.hide()
        self.TokenLine.hide()
        self.CreateChat.hide()

        self.leave.show()
        self.nicktext.show()
        self.entertext.show()
        self.sendbtn.show()
        self.nickname.show()
        self.msges.show()
        self.msges.moveCursor(QtGui.QTextCursor.End)
        self.msges.ensureCursorVisible()

    def send_message(self):
        # Take a current UTC time \ Получаем текущее время UTC
        current_time = datetime.utcnow().strftime('%H:%M')
        # Replace an empty nickname with 'Аноним' \ Заменяем пустой ник ником 'Аноним'
        if self.nickname.toPlainText() == '':
            self.nickname.setPlainText('Аноним')
        # Prohibition on sending an empty message \ Запрет на отправку пустого сообщения
        if self.entertext.toPlainText().strip() != '':
            message = f'[{current_time}] {self.nickname.toPlainText()}: {self.entertext.toPlainText()}'
            requests.get(f'{base_url}/chat?token={token}&msg={message.strip()}')
            self.entertext.setPlainText('')

    def leave_chat(self):
        global token
        global last_msg
        # Notification when user left from chat \ Уведомление, когда пользователь вышел из чата
        current_time = datetime.utcnow().strftime('%H:%M')
        message = f'[{current_time}] {self.nickname.toPlainText()} покинул чат'
        requests.get(f'{base_url}/chat?token={token}&msg={message.strip()}')
        # Token values and last_msg are reset \ Переменные token и last_msg сбрасываются
        token = ''
        last_msg = ''
        # The chat interface is hidden, the join chat interface appears
        # Интерфейс чата скрывается, появляется интерфейс присоединения к чату
        self.leave.hide()
        self.nicktext.hide()
        self.entertext.hide()
        self.sendbtn.hide()
        self.nickname.hide()
        self.msges.hide()

        self.logo.show()
        self.GoToTheChat.show()
        self.WriteTokenText.show()
        self.TokenLine.show()
        self.TokenLine.setAlignment(QtCore.Qt.AlignCenter)
        self.CreateChat.show()

    # Function for displaying new messages in chat \ Функция отображения новых сообщений в чате
    def update_messages(self, message):
        new_text = [self.msges.toPlainText()][0]
        if '\n' == [self.msges.toPlainText()][0][0]:
            new_text = [self.msges.toPlainText()][0][1:]
        new_text += message + '\n'
        self.msges.setPlainText(new_text)
        self.msges.moveCursor(QtGui.QTextCursor.End)
        self.msges.ensureCursorVisible()

    # When closing a window, checking whether the user is in the chat If yes, then he leaves him
    # Проверка при закрытии окна, находиться ли пользователь в чате если да, то он покидает его
    def closeEvent(self, event):
        if token != '':
            self.leave_chat()

    # Opening the window about the program
    # Открытие окна о программе
    def about(self):
        self.about_window.show()


class AboutWindow(QtWidgets.QWidget):
    def __init__(self):
        super(AboutWindow, self).__init__()
        self.setFixedSize(680, 190)
        self.setWindowTitle('О программе')
        self.github = QtWidgets.QToolButton(self)
        self.github.setGeometry(QtCore.QRect(30, 125, 625, 50))
        self.github.setText("Посетить Git Hub")
        self.github.clicked.connect(gitopen)
        self.disc = QtWidgets.QLabel(self)
        self.disc.setGeometry(QtCore.QRect(35, 15, 621, 100))
        self.disc.setText("Перетирач - это анонимны мессенджер, разработанный при помощи PyQt, который\n"
                          "представляет пользователям среду для обмена текстовыми сообщениями.\n"
                          "Благодаря использованию токенов для входа в чаты отпадает необходимость в регистрации,\n"
                          "обеспечивается анонимность и приватность.\n\nВерсия: 1.0")


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    # Application icon loading \ Загрузка значка приложения
    byte_array = QtCore.QByteArray(requests.get(f'{base_url}take_ico').content)
    pixmap = QtGui.QPixmap()
    success = pixmap.loadFromData(byte_array)
    app.setWindowIcon(QtGui.QIcon(pixmap))
    ui = MainWindow()
    ui.setup_ui()
    ui.show()
    sys.exit(app.exec_())
