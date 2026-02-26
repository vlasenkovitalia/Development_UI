import tkinter as tk
from tkinter import messagebox, simpledialog
from enum import auto, Enum
from typing import Optional, Generator, Tuple
from collections import deque
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class BasicDirections(Enum):
    N = auto()
    S = auto()
    W = auto()
    E = auto()
    NW = auto()
    SE = auto()

class RobotDirections(Enum):
    LAVA_FORWARD = auto()
    RETREAT = auto()
    SHIFT_LEFT = auto()
    SHIFT_RIGHT = auto()
    DIAG_UP = auto()
    DIAG_DOWN = auto()

class SideDirection:
    def __init__(self, side: BasicDirections, direction: RobotDirections):
        self.side = side
        self.direction = direction

SIDE_DIRECTION_1 = SideDirection(BasicDirections.N, RobotDirections.LAVA_FORWARD)
SIDE_DIRECTION_2 = SideDirection(BasicDirections.S, RobotDirections.RETREAT)
SIDE_DIRECTION_3 = SideDirection(BasicDirections.W, RobotDirections.SHIFT_LEFT)
SIDE_DIRECTION_4 = SideDirection(BasicDirections.E, RobotDirections.SHIFT_RIGHT)
SIDE_DIRECTION_5 = SideDirection(BasicDirections.NW, RobotDirections.DIAG_UP)
SIDE_DIRECTION_6 = SideDirection(BasicDirections.SE, RobotDirections.DIAG_DOWN)

class MethodDirection:
    def __init__(self, method_name: str, direction_value: int):
        self.method_name = method_name
        self.direction_value = direction_value

METHOD_DIRECTION_1 = MethodDirection("ЕхатьКЗоне", RobotDirections.LAVA_FORWARD.value)
METHOD_DIRECTION_2 = MethodDirection("Отойти", RobotDirections.RETREAT.value)
METHOD_DIRECTION_3 = MethodDirection("СдвинутьВлево", RobotDirections.SHIFT_LEFT.value)
METHOD_DIRECTION_4 = MethodDirection("СдвинутьВправо", RobotDirections.SHIFT_RIGHT.value)
METHOD_DIRECTION_5 = MethodDirection("Подняться", RobotDirections.DIAG_UP.value)
METHOD_DIRECTION_6 = MethodDirection("Спуститься", RobotDirections.DIAG_DOWN.value)


class PolygonCellType(Enum):
    LAVA = auto()
    STONE = auto()
    SOIL = auto()
    TEST_TUBE = auto()
    ASH = auto()
    BARRIER = auto()
    FINISH = auto()


class PolygonCell:
    def __init__(self, has_robot: bool, cell_type: PolygonCellType, x: int = 0, y: int = 0):
        self.has_robot = has_robot
        self.cell_type = cell_type
        self.x = x
        self.y = y


class Polygon:
    def __init__(self, width: int, length: int, cells: Optional[list[list[PolygonCell]]] = None):
        self.width = width
        self.length = length
        if cells:
            self.cells = cells
        else:
            self.cells = [[PolygonCell(False, PolygonCellType.LAVA, x, y) for y in range(self.length)] for x in range(self.width)]

    def init_polygon(self, cell_type: PolygonCellType):
        for x in range(self.width):
            for y in range(self.length):
                cell = self.cells[x][y]
                cell.x = x
                cell.y = y
                cell.cell_type = cell_type

    def set_cell_type(self, x: int, y: int, cell_type: PolygonCellType):
        if 0 <= x < self.width and 0 <= y < self.length:
            self.cells[x][y].cell_type = cell_type

    def get_next_cell(self, current_cell: PolygonCell, search_direction: int) -> Optional[PolygonCell]:
        direction = RobotDirections(search_direction)
        dx, dy = 0, 0

        if direction == RobotDirections.LAVA_FORWARD:
            dy = 1
        elif direction == RobotDirections.RETREAT:
            dy = -1
        elif direction == RobotDirections.SHIFT_LEFT:
            dx = -1
        elif direction == RobotDirections.SHIFT_RIGHT:
            dx = 1
        elif direction == RobotDirections.DIAG_UP:
            dx, dy = -1, 1
        elif direction == RobotDirections.DIAG_DOWN:
            dx, dy = 1, -1

        new_x = current_cell.x + dx
        new_y = current_cell.y + dy

        if 0 <= new_x < self.width and 0 <= new_y < self.length:
            return self.cells[new_x][new_y]
        return None

    def get_snake_iterator(self):
        return SnakeIterator(self)


class SnakeIterator:
    def __init__(self, polygon: Polygon):
        self.width = polygon.width
        self.length = polygon.length
        self.polygon = polygon
        self.x = 0
        self.y = 0
        self.direction = "RIGHT"
        self.first = True

    def __iter__(self):
        return self

    def __next__(self) -> PolygonCell:
        if self.first:
            self.first = False
            return self.polygon.cells[self.x][self.y]

        if self.direction == "RIGHT":
            if self.x + 1 < self.width:
                self.x += 1
            else:
                if self.y + 1 >= self.length:
                    raise StopIteration
                self.y += 1
                self.direction = "LEFT"
        else:
            if self.x - 1 >= 0:
                self.x -= 1
            else:
                if self.y + 1 >= self.length:
                    raise StopIteration
                self.y += 1
                self.direction = "RIGHT"

        return self.polygon.cells[self.x][self.y]


class RobotVulcano:
    def __init__(self, polygon: Polygon):
        self.polygon = polygon
        self.current_cell = self._find_robot_cell()
        self.current_cell.has_robot = True
        self.path = [self.current_cell]

    def _find_robot_cell(self) -> PolygonCell:
        for x in range(self.polygon.width):
            for y in range(self.polygon.length):
                cell = self.polygon.cells[x][y]
                if cell.has_robot:
                    return cell
        # Если робот не найден, помещаем его в (0,0) и устанавливаем флаг
        cell = self.polygon.cells[0][0]
        cell.has_robot = True
        return cell

    def move_forward(self):
        return self._move(METHOD_DIRECTION_1.direction_value)

    def move_backward(self):
        return self._move(METHOD_DIRECTION_2.direction_value)

    def move_left(self):
        return self._move(METHOD_DIRECTION_3.direction_value)

    def move_right(self):
        return self._move(METHOD_DIRECTION_4.direction_value)

    def move_diag_up(self):
        return self._move(METHOD_DIRECTION_5.direction_value)

    def move_diag_down(self):
        return self._move(METHOD_DIRECTION_6.direction_value)

    def stone(self):
        if self.current_cell.cell_type == PolygonCellType.STONE:
            self.current_cell.cell_type = PolygonCellType.SOIL

    def soil(self):
        if self.current_cell.cell_type == PolygonCellType.SOIL:
            self.current_cell.cell_type = PolygonCellType.TEST_TUBE

    def _move(self, direction_value: int):
        next_cell = self.polygon.get_next_cell(self.current_cell, direction_value)
        if next_cell is None:
            return None
        if next_cell.cell_type in (PolygonCellType.ASH, PolygonCellType.BARRIER):
            return None

        self.current_cell.has_robot = False
        next_cell.has_robot = True
        self.current_cell = next_cell
        self.path.append(self.current_cell)
        return next_cell

    def get_neighbors(self, cell):
        neighbors = []
        for dir_value in [d.value for d in RobotDirections]:
            next_cell = self.polygon.get_next_cell(cell, dir_value)
            if next_cell and next_cell.cell_type not in (PolygonCellType.ASH, PolygonCellType.BARRIER):
                neighbors.append(next_cell)
        return neighbors

    def bfs_path(self, start, goal):
        if start == goal:
            return [start]
        visited = set()
        queue = deque()
        queue.append((start, [start]))
        visited.add((start.x, start.y))
        while queue:
            current, path = queue.popleft()
            for neighbor in self.get_neighbors(current):
                if (neighbor.x, neighbor.y) not in visited:
                    if neighbor == goal:
                        return path + [neighbor]
                    visited.add((neighbor.x, neighbor.y))
                    queue.append((neighbor, path + [neighbor]))
        return None

    def _move_towards(self, target_cell):
        dx = target_cell.x - self.current_cell.x
        dy = target_cell.y - self.current_cell.y

        dir_map = {
            (0, 1): RobotDirections.LAVA_FORWARD,
            (0, -1): RobotDirections.RETREAT,
            (-1, 0): RobotDirections.SHIFT_LEFT,
            (1, 0): RobotDirections.SHIFT_RIGHT,
            (-1, 1): RobotDirections.DIAG_UP,
            (1, -1): RobotDirections.DIAG_DOWN
        }

        move_methods = {
            RobotDirections.LAVA_FORWARD: self.move_forward,
            RobotDirections.RETREAT: self.move_backward,
            RobotDirections.SHIFT_LEFT: self.move_left,
            RobotDirections.SHIFT_RIGHT: self.move_right,
            RobotDirections.DIAG_UP: self.move_diag_up,
            RobotDirections.DIAG_DOWN: self.move_diag_down
        }

        key = (dx, dy)
        if key in dir_map:
            direction = dir_map[key]
            method = move_methods[direction]
            result = method()
            if result is None:
                raise Exception(f"Move failed from ({self.current_cell.x},{self.current_cell.y}) to ({target_cell.x},{target_cell.y})")
        else:
            raise Exception(f"Invalid move delta: ({dx}, {dy})")

    def work_generator(self) -> Generator[Tuple[str, PolygonCell], None, None]:
        """Генерирует шаги работы робота. Каждый шаг — кортеж (тип_действия, ячейка)."""
        targets = []
        finish_cell = None
        for cell in self.polygon.get_snake_iterator():
            if cell.cell_type in (PolygonCellType.STONE, PolygonCellType.SOIL):
                targets.append(cell)
            elif cell.cell_type == PolygonCellType.FINISH:
                finish_cell = cell

        if self.current_cell in targets:
            if self.current_cell.cell_type == PolygonCellType.STONE:
                self.stone()
                yield ('stone', self.current_cell)
                self.soil()
                yield ('soil', self.current_cell)
            elif self.current_cell.cell_type == PolygonCellType.SOIL:
                self.soil()
                yield ('soil', self.current_cell)
            targets.remove(self.current_cell)

        while targets:
            best_path = None
            for target in targets:
                path = self.bfs_path(self.current_cell, target)
                if path and (best_path is None or len(path) < len(best_path)):
                    best_path = path

            if best_path is None:
                print("Внимание: нет пути к оставшимся целям")
                break

            for cell in best_path[1:]:
                self._move_towards(cell)
                yield ('move', cell)
                if self.current_cell in targets:
                    if self.current_cell.cell_type == PolygonCellType.STONE:
                        self.stone()
                        yield ('stone', self.current_cell)
                        self.soil()
                        yield ('soil', self.current_cell)
                    elif self.current_cell.cell_type == PolygonCellType.SOIL:
                        self.soil()
                        yield ('soil', self.current_cell)
                    targets.remove(self.current_cell)

        if finish_cell:
            path_to_finish = self.bfs_path(self.current_cell, finish_cell)
            if path_to_finish:
                for cell in path_to_finish[1:]:
                    self._move_towards(cell)
                    yield ('move', cell)
            yield ('finish', finish_cell)
        else:
            print("Клетка FINISH не найдена")
            yield ('finish', None)


class RobotVulcanoGUI:
    COLORS = {
        PolygonCellType.LAVA: "dark orange",
        PolygonCellType.STONE: "gray",
        PolygonCellType.SOIL: "sienna4",
        PolygonCellType.TEST_TUBE: "deep sky blue",
        PolygonCellType.ASH: "dark gray",
        PolygonCellType.BARRIER: "black",
        PolygonCellType.FINISH: "chartreuse2",
    }

    TYPE_NAMES_RU = {
        PolygonCellType.LAVA: "Лава",
        PolygonCellType.STONE: "Камень",
        PolygonCellType.SOIL: "Почва",
        PolygonCellType.TEST_TUBE: "Пробирка",
        PolygonCellType.ASH: "Пепел",
        PolygonCellType.BARRIER: "Барьер",
        PolygonCellType.FINISH: "Финиш",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Робот-вулканолог")

        self.is_animating = False
        self.work_gen = None
        self.animation_id = None

        # Загружаем изображение робота, если возможно
        self.robot_image = None
        self.load_robot_image()

        # Полигон и робот (инициализация демонстрационным примером)
        self.polygon = Polygon(5, 6)
        self.init_test_polygon()

        self.robot = RobotVulcano(self.polygon)

        self.finish_cell = None
        self._find_finish_cell()

        # Основной контейнер
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть: сетка и легенда
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Сетка
        self.grid_frame = tk.Frame(left_frame)
        self.grid_frame.pack()

        # Легенда
        legend_frame = tk.LabelFrame(left_frame, text="Легенда", padx=5, pady=5)
        legend_frame.pack(pady=10, fill=tk.X)
        self.create_legend(legend_frame)

        # Правая часть: управление
        self.control_frame = tk.Frame(main_frame)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.create_control_panel()

        self.cells_widgets = []
        self.draw_grid()

        self.update_info()

    def _find_finish_cell(self):
        """Находит клетку финиша в полигоне."""
        for x in range(self.polygon.width):
            for y in range(self.polygon.length):
                if self.polygon.cells[x][y].cell_type == PolygonCellType.FINISH:
                    self.finish_cell = self.polygon.cells[x][y]
                    return
        self.finish_cell = None

    def load_robot_image(self):
        """Загружает изображение робота из файла robot.png, если возможно."""
        if not PIL_AVAILABLE:
            print("Pillow не установлен, используется кружок")
            return
        if not os.path.exists("robot.png"):
            print("Файл robot.png не найден, используется кружок")
            return
        try:
            img = Image.open("robot.png")
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            self.robot_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Ошибка загрузки robot.png: {e}")
            self.robot_image = None

    def create_legend(self, parent):
        """Создаёт легенду с цветами и названиями типов."""
        for cell_type in PolygonCellType:
            frame = tk.Frame(parent)
            frame.pack(anchor=tk.W, pady=2)
            color_box = tk.Canvas(frame, width=20, height=20, bg=self.COLORS[cell_type],
                                   highlightthickness=1, highlightbackground="black")
            color_box.pack(side=tk.LEFT, padx=5)
            label = tk.Label(frame, text=self.TYPE_NAMES_RU[cell_type])
            label.pack(side=tk.LEFT)

    def init_test_polygon(self):
        """Инициализация полигона примером."""
        self.polygon.set_cell_type(0, 0, PolygonCellType.STONE)
        self.polygon.set_cell_type(1, 0, PolygonCellType.FINISH)
        self.polygon.set_cell_type(2, 2, PolygonCellType.SOIL)
        self.polygon.set_cell_type(3, 3, PolygonCellType.BARRIER)
        self.polygon.set_cell_type(4, 5, PolygonCellType.ASH)

    def draw_grid(self):
        """Отрисовывает сетку ячеек на Canvas."""
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.cells_widgets = []
        cell_size = 50

        for y in range(self.polygon.length - 1, -1, -1):
            row_widgets = []
            for x in range(self.polygon.width):
                canvas = tk.Canvas(self.grid_frame, width=cell_size, height=cell_size,
                                    bg=self.COLORS[self.polygon.cells[x][y].cell_type],
                                    highlightthickness=1, highlightbackground="black")
                canvas.grid(row=self.polygon.length - 1 - y, column=x, padx=1, pady=1)
                canvas.cell = self.polygon.cells[x][y]
                canvas.bind("<Button-1>", lambda e, cx=x, cy=y: self.on_cell_click(cx, cy))
                row_widgets.append(canvas)
            self.cells_widgets.append(row_widgets)

        self.draw_robots()

    def draw_robots(self):
        """Рисует изображение робота на соответствующей ячейке."""
        for row in self.cells_widgets:
            for canvas in row:
                canvas.delete("robot")

        if self.robot and self.robot.current_cell:
            x, y = self.robot.current_cell.x, self.robot.current_cell.y
            canvas = self.cells_widgets[self.polygon.length - 1 - y][x]
            if self.robot_image:
                canvas.create_image(25, 25, image=self.robot_image, tags="robot")
            else:
                canvas.create_oval(10, 10, 40, 40, fill="red", outline="darkred", width=2, tags="robot")

    def on_cell_click(self, x, y):
        """Обработка клика по ячейке: изменение типа или установка робота."""
        if self.is_animating:
            messagebox.showinfo("Анимация", "Дождитесь завершения анимации")
            return

        top = tk.Toplevel(self.root)
        top.title("Действие с ячейкой")
        top.geometry("250x400")
        tk.Label(top, text=f"Ячейка ({x}, {y})").pack(pady=5)

        def set_type(cell_type):
            # Проверка на уникальность финиша
            if cell_type == PolygonCellType.FINISH:
                if self.finish_cell and (self.finish_cell.x != x or self.finish_cell.y != y):
                    # Спрашиваем подтверждение на замену
                    if not messagebox.askyesno("Замена финиша", "Финиш уже существует. Заменить его на этой клетке?"):
                        return
                    # Убираем старый финиш
                    self.finish_cell.cell_type = PolygonCellType.LAVA
                    old_canvas = self.cells_widgets[self.polygon.length - 1 - self.finish_cell.y][self.finish_cell.x]
                    old_canvas.config(bg=self.COLORS[PolygonCellType.LAVA])
                # Устанавливаем новый финиш
                self.finish_cell = self.polygon.cells[x][y]

            # Если текущая клетка была финишем, а новый тип не финиш, обнуляем ссылку
            if self.finish_cell and self.finish_cell.x == x and self.finish_cell.y == y and cell_type != PolygonCellType.FINISH:
                self.finish_cell = None

            # Изменяем тип клетки
            self.polygon.set_cell_type(x, y, cell_type)
            canvas = self.cells_widgets[self.polygon.length - 1 - y][x]
            canvas.config(bg=self.COLORS[cell_type])

            # Если на этой клетке стоит робот, обновляем его тип
            if self.robot.current_cell.x == x and self.robot.current_cell.y == y:
                self.robot.current_cell.cell_type = cell_type

            self.draw_robots()
            self.update_info()
            top.destroy()

        def set_robot():
            """Устанавливает робота в эту клетку."""
            cell = self.polygon.cells[x][y]
            # Проверяем, можно ли поставить робота (не на барьер/пепел)
            if cell.cell_type in (PolygonCellType.ASH, PolygonCellType.BARRIER):
                messagebox.showerror("Ошибка", "Нельзя поставить робота на непроходимую клетку")
                return

            # Убираем робота со старой позиции
            self.robot.current_cell.has_robot = False
            # Ставим на новую
            cell.has_robot = True
            self.robot.current_cell = cell
            self.robot.path = [cell]  # сбрасываем путь
            self.draw_robots()
            self.update_info()
            top.destroy()

        # Кнопки для каждого типа ячеек
        for t in PolygonCellType:
            btn = tk.Button(top, text=self.TYPE_NAMES_RU[t], bg=self.COLORS[t],
                            command=lambda tt=t: set_type(tt))
            btn.pack(fill=tk.X, padx=5, pady=2)

        # Отдельная кнопка для установки робота
        tk.Button(top, text="Установить робота сюда", command=set_robot,
                  bg="lightblue").pack(fill=tk.X, padx=5, pady=5)

    def create_control_panel(self):
        """Создаёт панель с кнопками управления."""
        self.info_var = tk.StringVar()
        info_label = tk.Label(self.control_frame, textvariable=self.info_var,
                              font=("Arial", 10), justify=tk.LEFT)
        info_label.pack(pady=5)

        # Кнопки движений
        move_frame = tk.LabelFrame(self.control_frame, text="Движение")
        move_frame.pack(fill=tk.X, pady=5)

        tk.Button(move_frame, text="Ехать к зоне (вперёд)", command=self.cmd_forward).pack(fill=tk.X)
        tk.Button(move_frame, text="Отойти (назад)", command=self.cmd_backward).pack(fill=tk.X)
        tk.Button(move_frame, text="Сдвинуть влево", command=self.cmd_left).pack(fill=tk.X)
        tk.Button(move_frame, text="Сдвинуть вправо", command=self.cmd_right).pack(fill=tk.X)
        tk.Button(move_frame, text="Подняться (диаг. вверх)", command=self.cmd_diag_up).pack(fill=tk.X)
        tk.Button(move_frame, text="Спуститься (диаг. вниз)", command=self.cmd_diag_down).pack(fill=tk.X)

        # Кнопки действий
        action_frame = tk.LabelFrame(self.control_frame, text="Действия")
        action_frame.pack(fill=tk.X, pady=5)

        tk.Button(action_frame, text="Камень", command=self.cmd_stone).pack(fill=tk.X)
        tk.Button(action_frame, text="Почва", command=self.cmd_soil).pack(fill=tk.X)
        tk.Button(action_frame, text="Автоматическая работа (work)", command=self.cmd_work_animated).pack(fill=tk.X)

        # Кнопки управления лабиринтом
        edit_frame = tk.LabelFrame(self.control_frame, text="Редактор")
        edit_frame.pack(fill=tk.X, pady=5)

        tk.Button(edit_frame, text="Новый лабиринт", command=self.cmd_new).pack(fill=tk.X)
        tk.Button(edit_frame, text="Очистить (всё в лаву)", command=self.cmd_clear).pack(fill=tk.X)

        tk.Button(self.control_frame, text="Выход", command=self.root.quit).pack(pady=10)

    def update_info(self):
        """Обновляет информационную панель."""
        cell = self.robot.current_cell
        text = (f"Позиция: ({cell.x}, {cell.y})\n"
                f"Тип: {self.TYPE_NAMES_RU[cell.cell_type]}\n"
                f"Длина пути: {len(self.robot.path)}")
        self.info_var.set(text)

    def refresh_display(self):
        """Перерисовывает сетку и робота."""
        for row in self.cells_widgets:
            for canvas in row:
                canvas.config(bg=self.COLORS[canvas.cell.cell_type])
        self.draw_robots()
        self.update_info()
        self.root.update_idletasks()

    def cmd_forward(self):
        if self.is_animating:
            return
        if self.robot.move_forward():
            self.refresh_display()
        else:
            messagebox.showerror("Ошибка", "Невозможно двигаться вперёд")

    def cmd_backward(self):
        if self.is_animating:
            return
        if self.robot.move_backward():
            self.refresh_display()
        else:
            messagebox.showerror("Ошибка", "Невозможно двигаться назад")

    def cmd_left(self):
        if self.is_animating:
            return
        if self.robot.move_left():
            self.refresh_display()
        else:
            messagebox.showerror("Ошибка", "Невозможно двигаться влево")

    def cmd_right(self):
        if self.is_animating:
            return
        if self.robot.move_right():
            self.refresh_display()
        else:
            messagebox.showerror("Ошибка", "Невозможно двигаться вправо")

    def cmd_diag_up(self):
        if self.is_animating:
            return
        if self.robot.move_diag_up():
            self.refresh_display()
        else:
            messagebox.showerror("Ошибка", "Невозможно двигаться по диагонали вверх")

    def cmd_diag_down(self):
        if self.is_animating:
            return
        if self.robot.move_diag_down():
            self.refresh_display()
        else:
            messagebox.showerror("Ошибка", "Невозможно двигаться по диагонали вниз")

    def cmd_stone(self):
        if self.is_animating:
            return
        self.robot.stone()
        self.refresh_display()

    def cmd_soil(self):
        if self.is_animating:
            return
        self.robot.soil()
        self.refresh_display()

    def cmd_work_animated(self):
        """Запускает анимированное выполнение work."""
        if self.is_animating:
            return
        self.is_animating = True
        self.work_gen = self.robot.work_generator()
        self.after_id = self.root.after(500, self.do_work_step)

    def do_work_step(self):
        """Выполняет один шаг анимации."""
        if not self.is_animating:
            return
        try:
            action, cell = next(self.work_gen)
            self.refresh_display()
            self.after_id = self.root.after(500, self.do_work_step)
        except StopIteration:
            self.is_animating = False
            self.after_id = None
            messagebox.showinfo("Завершено", "Работа робота завершена")
        except Exception as e:
            self.is_animating = False
            self.after_id = None
            messagebox.showerror("Ошибка", str(e))

    def cmd_new(self):
        """Создание нового лабиринта."""
        if self.is_animating:
            self.is_animating = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
        w = simpledialog.askinteger("Ширина", "Введите ширину:", minvalue=1, maxvalue=20)
        if not w:
            return
        h = simpledialog.askinteger("Длина (высота)", "Введите длину (высоту):", minvalue=1, maxvalue=20)
        if not h:
            return
        self.polygon = Polygon(w, h)
        self.robot = RobotVulcano(self.polygon)
        self._find_finish_cell()  # найти финиш в новом полигоне
        self.draw_grid()
        self.refresh_display()

    def cmd_clear(self):
        """Заполнить весь лабиринт лавой."""
        if self.is_animating:
            self.is_animating = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
        for x in range(self.polygon.width):
            for y in range(self.polygon.length):
                self.polygon.cells[x][y].cell_type = PolygonCellType.LAVA
        self.finish_cell = None  # финиш удалён
        self.refresh_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = RobotVulcanoGUI(root)
    root.mainloop()