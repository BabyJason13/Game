import os
import sys
import pygame
from random import randint, choice
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QTableWidgetItem
from PyQt5.QtGui import QColor
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import csv


# Константы
WIDTH = 1000
HEIGHT = 600
COUNT_OF_KILLS = 0
GRAVITY = 1
NAME = ''

# Создание групп для первого монстрика. Новые создаю в фукнции Level
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
stars = pygame.sprite.Group()
sad = pygame.sprite.Group()
button_restart = pygame.sprite.Group()
button_start = pygame.sprite.Group()
screen_rect = (0, 0, WIDTH, HEIGHT)

# Список с изображенииями монстриков
PICTURES = ['monster1.png', 'monster2.png', 'monster3.png', 'monster4.png']

# Установка таймера
pygame.time.set_timer(pygame.USEREVENT, 1000)

# Настройка каналов
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
# Звук выстрела я выделил на отдельный канал, чтобы он мог проигрываться
# вместе с фоновой музыкой
gun_sound = pygame.mixer.Sound("data/gun_sound.wav")


# Дизайн таблицы результатов
class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(650, 433)
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 630, 413))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.tableWidget.setFont(font)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Таблица результатов"))


# Функция, отвечающая за загрузку изображения
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    #image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


# Фукнция, отвечающая за выход из программы
def terminate():
    pygame.quit()
    sys.exit()


# Класс, отвечающий за спрайты монстров
class Monster(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__(monster_group, all_sprites)
        self.image = load_image(image)
        self.mw = self.image.get_width()
        self.mh = self.image.get_height()
        # Данное условие нужно для расположения первого монстра на начальном экране
        if x != 780 and y != 0:
            self.x = randint(0, WIDTH - self.mw)
            self.y = randint(40, HEIGHT - self.mh - 150)
            self.rect = self.image.get_rect().move(self.x, self.y)
        else:
            self.rect = self.image.get_rect().move(780, 0)


class Restart(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(button_restart)
        self.image = pygame.Surface((50, 30))
        self.rect = pygame.Rect(950, 0, 100, 30)
        font = pygame.font.SysFont("Verdana", 12)
        text = font.render('New', 1, pygame.Color('white'))
        pygame.draw.rect(self.image, pygame.Color('white'), self.rect, 1)
        self.image.blit(text, (10, 9))


class Start(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(button_start)
        self.image = pygame.Surface((115, 35))
        self.rect = pygame.Rect(0, 0, 115, 35)
        font = pygame.font.SysFont("Verdana", 15)
        text = font.render('Начать играть', 1, pygame.Color('white'))
        pygame.draw.rect(self.image, pygame.Color('orange'), self.rect, 1)
        self.image.blit(text, (2, 10))


# Начальный экран
def start_screen():
    intro_text = ["ОХОТА НА МОНСТРОВ!   ПРАВИЛА ИГРЫ", "",
                  "Сегодня чудесный день для охоты на монстров, ",
                  "не так ли?",
                  "Убивай монстров на каждом уровне, но внимание!",
                  "с каждым уровнем все меньше времени и больше убийств",
                  "Для паузы нажимай правую стрелку",
                  'Для просмотра таблицы результатов жми Q',
                  "Ты со мной? Время не ждет!"]

    Start()
    fon = pygame.transform.scale(load_image('fon1.jpg'), (WIDTH, HEIGHT))
    Monster('monster1.png', 780, 0)
    screen.blit(fon, (0, 0))
    font = pygame.font.SysFont('Verdana', 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, (139, 0, 139))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    # Проигрывание фоновой музыки заставки
    pygame.mixer.music.load('data/start.mp3')
    pygame.mixer.music.play(-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                # Запуск просмотра csv-таблицы
                if event.key == pygame.K_q:
                    base = DataBase()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if 0 <= x <= 170 and 0 <= y <= 35:
                    pygame.mixer.music.stop()
                    return # начало игры
        button_start.draw(screen)
        monster_group.draw(screen)
        pygame.display.flip()


# Сколько секунд осталось
def mytime(seconds):
    font = pygame.font.SysFont('Verdana', 20)
    text = font.render(f"Осталось секунд: {seconds}", 1, (100, 255, 100))
    screen.blit(text, (20, 20))


# Сколько убито монстров
def killscount(count):
    font = pygame.font.SysFont('Verdana', 20)
    text = font.render(f"Убийств: {count}", 1, (100, 255, 100))
    screen.blit(text, (400, 20))


# Сколько осталось убить монстров
def leftkills(count):
    font = pygame.font.SysFont('Verdana', 20)
    if count >= 0:
        text = font.render(f"Осталось убить: {count}", 1, (100, 255, 100))
    else:
        text = font.render(f"Осталось убить: 0", 1, (100, 255, 100))
    screen.blit(text, (650, 20))


# Текст "уровень пройден"
def nextlevel():
    font = pygame.font.SysFont('Verdana', 60)
    text = font.render("УРОВЕНЬ ПРОЙДЕН", 1, (100, 255, 100))
    screen.blit(text, (200, 300))
    pygame.display.update()


# Текст "игра окончена"
def text_gameover():
    font = pygame.font.SysFont('Verdana', 60)
    text = font.render("ИГРА ОКОНЧЕНА", 1, (100, 255, 100))
    screen.blit(text, (230, 300))
    pygame.display.update()


# Функция отвечает за выстрел
def blood(x, y):
    image = load_image("blood.png")
    # Пауза фоновой музыки -> проигрыш выстрела -> возобновление фоновой музыки
    pygame.mixer.music.pause()
    gun_sound.play()
    pygame.mixer.music.unpause()

    imagew = image.get_width()
    imageh = image.get_height()
    screen.blit(image, (x - imagew / 2, y - imageh / 2))
    pygame.display.update()
    time.sleep(0.1)


# Текст паузы
def pausetext():
    font = pygame.font.SysFont('Verdana', 60)
    text = font.render("ПАУЗА", 1, (100, 255, 100))
    screen.blit(text, (400, 30))


# Универсальная функция для уровней игры
def Level(background, n, seconds, countOfMonsters):
    # background - изображение файла (*.png)
    # n - количество монстров, возможных на экране
    # seconds - количество секунд на уровень
    # conutOfMonsters - сколько монстров нужно убить
    restart_button = Restart()
    monster_list = []
    monster_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    for i in range(n):
        monster = Monster(PICTURES[randint(0, 3)], 100, 100)
        monster_list.append(monster)

    fon = pygame.transform.scale(load_image(background), (WIDTH, HEIGHT))
    gun = load_image('gun3.png')
    arrow = load_image("arrow_small.png")
    count = 0

    # pause и running - переменные, которые отвечают за паузу и процесс игры соответственно.
    # игра находится в том положении, в котором находится переменная state
    pause, running = False, True
    state = running

    pygame.mixer.music.load('data/main_sound.mp3')
    pygame.mixer.music.play(-1)

    while True:
        if state == running:
            x, y = pygame.mouse.get_pos()
            screen.blit(fon, (0, 0))
            for i in range(n):
                screen.blit(monster_list[i].image,
                            (monster_list[i].x, monster_list[i].y))

            # Расположение оружия и курсора - прицела
            button_restart.draw(screen)
            screen.blit(gun, (x, 450))
            screen.blit(arrow, (x - arrow.get_width() / 2, y - arrow.get_height() / 2))
            arrow_r = pygame.Rect(x - arrow.get_width() / 2, y - arrow.get_height() / 2, arrow.get_width(),
                                  arrow.get_height())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Флаг нужен для того, чтобы пресекать возможность убийства сразу нескольких монстров
                    # Проверка на столкновение с монстрами. Если оба условия верны, то
                    # убираем монстра с экрана. Если флаг == 1, то убийство произошло, а
                    # больше одного монстра убить невозможно
                    if arrow_r.colliderect(restart_button):
                        return 2
                    else:
                        flag = 0
                        for i in range(n):
                            if arrow_r.colliderect(monster_list[i]) and flag == 0:
                                blood(monster_list[i].x + monster_list[i].mw / 2,
                                           monster_list[i].y + monster_list[i].mh / 2)
                                all_sprites.remove(monster_list[i])
                                monster_group.remove(monster_list[i])
                                del monster_list[i]
                                monster = Monster(PICTURES[randint(0, 3)], 100, 100)
                                monster_list.append(monster)
                                count += 1
                                flag = 1
                if event.type == pygame.USEREVENT:
                    # Каждую секунду становится все меньше и меньше времени
                    seconds -= 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        # будет пауза
                        pygame.mixer.music.pause()
                        state = pause
            # Расположения остатка секунд, сколько нужно убить и сколько уже убито монстров
            mytime(seconds)
            killscount(count)
            leftkills(countOfMonsters - count)
            if seconds == 0:
                pygame.display.update()
                pygame.mixer.music.stop()
                if count >= countOfMonsters:
                    return 0, count
                else:
                    return 1, count
            all_sprites.draw(screen)
            all_sprites.update()
        elif state == pause:
            pygame.display.flip()
            for event in pygame.event.get():
                # Если условие выполнится, то игра продолжается
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    pygame.mixer.music.unpause()
                    state = running
            pausetext()
        pygame.display.flip()


# Запись результатов в таблицу
def my_writer(reader, new_row):
    with open('data/results.csv', 'w', newline='\n', encoding='utf8') as csvfile:
        csvfile.write('')
        row = f'{reader[0][0]};{reader[0][1]};{reader[0][2]}\n'
        csvfile.write(row)
        for row in reader[1:]:
            row = f'{row[0]};{str(row[1])};{str(row[2])}\n'
            csvfile.write(row)
        if new_row != ' ':
            csvfile.write(new_row)


# Считывание данных таблицы
def results(NAME, COUNT_OF_KILLS, win):
    flag = 'No'
    # Считывание данных
    with open('data/results.csv', encoding="utf8") as csvfile:
        reader = list(csv.reader(csvfile, delimiter=';', quotechar='"'))
    # Преобразуем кол-во монстров в тип int
    for elem in reader[1:]:
        elem[1] = int(elem[1])
        elem[2] = int(elem[2])
    for elem in reader[1:]:
        # Если победивший есть в csv-файле, то в методе my_writer идет запись
        # количества убитых монстров в общем + за эту игру и результат игры:
        # победа или поражение
        if elem[0] == NAME:
            flag = 'Yes'
            elem[1] += COUNT_OF_KILLS
            elem[2] += win
            my_writer(reader, ' ')
            break
    # Победившего в таблице не оказалось. Записываем его имя и количество убийств в файл
    if flag == 'No':
        my_writer(reader, f'{NAME};{COUNT_OF_KILLS};{win}\n')


# Диалоговое окно
class MyDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        global NAME
        while NAME == '':
            NAME, okBtnPressed = QInputDialog.getText(self,
                                                      "Введите имя", "Как тебя зовут?")
        if okBtnPressed:
            return


# Класс, отвечающий за открытие таблицы результатов
class DataBase(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.loadTable('data/results.csv')
        self.show()

    # Красим имена и результат топ-3 игроков
    def colorRow(self, row, color):
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.item(row, i).setBackground(color)

    # Вывод игроков
    def loadTable(self, name):
        with open(name, encoding="utf8") as csvfile:
            reader = list(csv.reader(csvfile, delimiter=';', quotechar='"'))
            title = reader[0]
            # Сортировка по количеству побед
            reader = sorted(reader[1:], key=lambda x: -int(x[2]))

            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setHorizontalHeaderLabels(title)
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(reader):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(elem))
                if i < 3:
                    self.colorRow(i, QColor(randint(0, 255), randint(0, 255), randint(0, 255)))

        self.tableWidget.resizeColumnsToContents()


# Класс для отображения частиц
class Particle(pygame.sprite.Sprite):
    def __init__(self, name, pos, dx, dy):
        if name == 'star.png':
            super().__init__(stars)
        else:
            super().__init__(sad)
        fire = [load_image(name)]
        for scale in (5, 10, 20):
            fire.append(pygame.transform.scale(fire[0], (scale, scale)))
        self.image = choice(fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


# Создание частиц
def create_particles(position, win):
    # количество создаваемых частиц
    particle_count = 120
    # возможные скорости
    numbers = range(-15, 16)
    if win:
        name = 'star.png'
    else:
        name = 'sad.png'
    for _ in range(particle_count):
        Particle(name, position, choice(numbers), choice(numbers))


# Фукнция, отвечающая за проигрышное окончание игры: запись результатов,
# отображение фоновой картинки и частицы - грустные смайлики
def new_gameover():
    Restart()
    text_gameover()
    time.sleep(3)
    results(NAME, COUNT_OF_KILLS, 0)
    gameover = load_image('gameover.png')
    pygame.display.update()

    pygame.mixer.music.load('data/lost.mp3')
    pygame.mixer.music.play(-1)

    pygame.mouse.set_visible(True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if 1000 >= x >= 950 and 30 >= y >= 0:
                    return 1
            if event.type == pygame.USEREVENT:
                # создаём частицы на рандомном месте раз в секунду
                create_particles([randint(0, WIDTH), randint(0, HEIGHT)], False)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    base = DataBase()
        screen.fill(pygame.Color("white"))
        screen.blit(gameover, (0, 0))
        button_restart.draw(screen)
        sad.draw(screen)
        sad.update()
        pygame.display.flip()
        clock.tick(20)


# Фукнция, отвечающая за победное окончание игры: запись результатов,
# отображение фоновой картинки и частицы - звездочки
def new_you_win():
    Restart()
    results(NAME, COUNT_OF_KILLS, 1)
    win = load_image('youwin.png')
    pygame.display.update()

    pygame.mixer.music.load('data/win.mp3')
    pygame.mixer.music.play(-1)

    pygame.mouse.set_visible(True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if 1000 >= x >= 950 and 30 >= y >= 0:
                    return 1
            if event.type == pygame.USEREVENT:
                # создаём частицы на рандомном месте раз в секунду
                create_particles([randint(0, WIDTH), randint(0, HEIGHT)], True)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    base = DataBase()

        screen.fill(pygame.Color("white"))
        screen.blit(win, (0, 0))
        button_restart.draw(screen)
        stars.draw(screen)
        stars.update()
        pygame.display.flip()
        clock.tick(20)


def game():
    global COUNT_OF_KILLS
    pygame.mouse.set_visible(False)

    COUNT_OF_KILLS = 0
    result1 = Level('background1.png', 2, 20, 20)
    # Уровень возвращает один либо два параметра:
    # 1 параметр: 2, если мы хотим заново начать всю игру
    # 2 параметра: 0 или 1 (победа или поражение) и
    # количество убитых монстров на уровне
    while result1 == 2:
        return game()
    COUNT_OF_KILLS += result1[1]
    if result1[0] == 0:
        nextlevel()
        time.sleep(5)
        result2 = Level('background2.png', 1, 25, 20)
        if result2 == 2:
            return game()
        COUNT_OF_KILLS += result2[1]
        if result2[0] == 0:
            nextlevel()
            time.sleep(5)
            result3 = Level('background3.png', 1, 15, 10)
            if result3 == 2:
                return game()
            COUNT_OF_KILLS += result3[1]
            if result3[0] == 0:
                nextlevel()
                time.sleep(3)
                win = new_you_win()
                if win == 1:
                    return game()
            else:
                g_o = new_gameover()
                if g_o == 1:
                    return game()
        else:
            g_o = new_gameover()
            if g_o == 1:
                return game()
    elif result1[0] == 1:
        g_o = new_gameover()
        if g_o == 1:
            return game()


if __name__ == '__main__':
    # Диалоговое окно с вводом имени
    app = QApplication(sys.argv)
    ex = MyDialog()
    # Создание экрана
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # Запуск заставки, далее - первого уровня
    start_screen()
    game()