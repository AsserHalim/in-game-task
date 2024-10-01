from pygame.base import init, quit
from pygame.constants import QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, K_BACKSPACE, K_SPACE
from pygame.display import set_mode, set_caption, flip
from pygame.surface import SurfaceType
from pygame.time import Clock
from pygame.event import get, Event
from pygame.mouse import get_pos, get_pressed
from pygame.draw import polygon, rect
from pygame.rect import Rect, RectType
from pygame.font import Font

from sys import exit
from typing import Optional, Tuple, List, Any, TextIO, Literal

# Initialize Pygame
init()

# Set up the display
WIDTH: int | float = 800
HEIGHT: int | float = 600
screen: SurfaceType = set_mode((WIDTH, HEIGHT))
set_caption("Enhanced Allocation Quest Game")

# Colors
WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
BLUE: tuple[int, int, int] = (0, 122, 255)
RED: tuple[int, int, int] = (255, 59, 48)
GREEN: tuple[int, int, int] = (52, 199, 89)
GRAY: tuple[int, int, int] = (142, 142, 147)
LIGHT_GRAY: tuple[int, int, int] = (209, 209, 214)
DARK_GRAY: tuple[int, int, int] = (50, 50, 50)

# Fonts
FONT: Font = Font(None, 32)
SMALL_FONT: Font = Font(None, 24)

# Game variables
level: int = 0
TOTAL_ITEMS: int = 50
MIN_ALLOCATION: int = 0
MAX_ALLOCATION: int = 50
LOG_FILE: str = "allocation_results.txt"


class Button:
    """
    A class to represent a clickable button in the game.
    """

    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: tuple[int, int, int]) -> None:
        self.rect: RectType = Rect(x, y, width, height)
        self.text: str = text
        self.color: tuple[int, int, int] = color
        self.active: bool = False

    def draw(self) -> None:
        """Draw the button on the screen."""
        rect(screen, self.color if not self.active else LIGHT_GRAY, self.rect, border_radius=10)
        rect(screen, DARK_GRAY, self.rect, 3, border_radius=10)
        if self.active:
            rect(screen, BLUE, self.rect.inflate(-4, -4), 3, border_radius=8)
        text_surf: SurfaceType = FONT.render(self.text, True, BLACK)
        text_rect: RectType = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_over(self, pos: tuple[int, int]) -> bool:
        """Check if the given position is over the button."""
        return self.rect.collidepoint(pos)


class ArrowButton:
    """
    A class to represent an arrow button for incrementing or decrementing values.
    """

    def __init__(self, x: int, y: int, width: int, height: int, direction: str) -> None:
        self.rect: RectType = Rect(x, y, width, height)
        self.direction: str = direction
        self.pressed: bool = False

    def draw(self) -> None:
        """Draw the arrow button on the screen."""
        color: tuple[int, int, int] = DARK_GRAY if self.pressed else GRAY
        rect(screen, color, self.rect, border_radius=5)
        if self.direction == 'up':
            polygon(screen, WHITE, [
                (self.rect.centerx, self.rect.top + 5),
                (self.rect.left + 5, self.rect.bottom - 5),
                (self.rect.right - 5, self.rect.bottom - 5)
            ])
        else:
            polygon(screen, WHITE, [
                (self.rect.centerx, self.rect.bottom - 5),
                (self.rect.left + 5, self.rect.top + 5),
                (self.rect.right - 5, self.rect.top + 5)
            ])

    def is_over(self, pos: tuple[int, int]) -> bool:
        """Check if the given position is over the button."""
        return self.rect.collidepoint(pos)


def draw_text(text: str, color: tuple[int, int, int], x: int, y: int, centered: bool = False) -> None:
    """
    Draw text on the screen.

    Args:
        text (str): The text to draw.
        color (Tuple[int, int, int]): The color of the text.
        x (int): The x-coordinate of the text.
        y (int): The y-coordinate of the text.
        centered (bool, optional): Whether to center the text. Defaults to False.
    """
    text_surface = FONT.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y)) if centered else (x, y)
    screen.blit(text_surface, text_rect)


def allocation_quest() -> Optional[list[int]]:
    """
    Run the allocation quest mini-game.

    Returns:
        Optional[List[int]]: The final allocations if confirmed, None if quit.
    """
    global level
    allocations: list[int] = [0, 0, 0]
    resource: str = "candy bars" if level % 4 == 0 else "blankets"

    input_buttons: list[Button] = [
        Button(WIDTH // 2 + 50, 160, 100, 40, "0", WHITE),
        Button(WIDTH // 2 + 50, 260, 100, 40, "0", WHITE),
        Button(WIDTH // 2 + 50, 360, 100, 40, "0", WHITE)
    ]

    arrow_buttons: list[list[ArrowButton]] = [
        [ArrowButton(WIDTH // 2 + 160, 160, 30, 20, 'up'), ArrowButton(WIDTH // 2 + 160, 180, 30, 20, 'down')],
        [ArrowButton(WIDTH // 2 + 160, 260, 30, 20, 'up'), ArrowButton(WIDTH // 2 + 160, 280, 30, 20, 'down')],
        [ArrowButton(WIDTH // 2 + 160, 360, 30, 20, 'up'), ArrowButton(WIDTH // 2 + 160, 380, 30, 20, 'down')]
    ]

    confirm_button: Button = Button(WIDTH // 2 - 50, 480, 100, 40, "Confirm", GREEN)
    active_input: Any = None
    clock: Clock = Clock()
    hold_time: int = 0
    hold_delay: int = 500
    hold_interval: int = 100

    while True:
        event: Event
        for event in get():
            if event.type == QUIT:
                return None
            if event.type == MOUSEBUTTONDOWN:
                pos: tuple[int, int] = get_pos()
                i: int
                button: Button
                for i, button in enumerate(input_buttons):
                    if button.is_over(pos):
                        active_input = i
                        btn: Button
                        for btn in input_buttons:
                            btn.active = False
                        button.active = True
                if confirm_button.is_over(pos) and sum(allocations) == TOTAL_ITEMS:
                    log_allocation_result(allocations)
                    return allocations
                i: int
                up: Any
                down: Any
                for i, (up, down) in enumerate(arrow_buttons):
                    if up.is_over(pos):
                        up.pressed = True
                        if sum(allocations) < TOTAL_ITEMS:
                            allocations[i] = min(allocations[i] + 1, MAX_ALLOCATION)
                    elif down.is_over(pos):
                        down.pressed = True
                        allocations[i] = max(allocations[i] - 1, MIN_ALLOCATION)
            if event.type == MOUSEBUTTONUP:
                row: list[ArrowButton]
                for row in arrow_buttons:
                    arrow: ArrowButton
                    for arrow in row:
                        arrow.pressed = False
            if event.type == KEYDOWN and active_input is not None:
                if event.key == K_BACKSPACE:
                    allocations[active_input] = allocations[active_input] // 10
                elif event.unicode.isdigit():
                    new_value = int(str(allocations[active_input]) + event.unicode)
                    allocations[active_input] = min(new_value, MAX_ALLOCATION)
                if sum(allocations) > TOTAL_ITEMS:
                    allocations[active_input] -= (sum(allocations) - TOTAL_ITEMS)

        mouse_buttons: tuple[bool, bool, bool] = get_pressed()
        if mouse_buttons[0]:
            pos = get_pos()
            i: int
            up: Any
            down: Any
            for i, (up, down) in enumerate(arrow_buttons):
                if up.is_over(pos) or down.is_over(pos):
                    hold_time += clock.get_time()
                    if hold_time > hold_delay:
                        if hold_time % hold_interval < 20:
                            if up.is_over(pos) and sum(allocations) < TOTAL_ITEMS:
                                allocations[i] = min(allocations[i] + 1, MAX_ALLOCATION)
                            elif down.is_over(pos):
                                allocations[i] = max(allocations[i] - 1, MIN_ALLOCATION)
                    break
            else:
                hold_time = 0
        else:
            hold_time = 0

        screen.fill(WHITE)
        draw_text(f"Level {level}: Allocate {TOTAL_ITEMS} {resource}", BLUE, WIDTH // 2, 80, centered=True)
        draw_text("My own inventory:", BLACK, WIDTH // 2 - 220, 170)
        draw_text("My group's inventory:", BLACK, WIDTH // 2 - 220, 270)
        draw_text("Other group's inventory:", BLACK, WIDTH // 2 - 220, 370)

        i: int
        button: Button
        for i, button in enumerate(input_buttons):
            button.text = str(allocations[i])
            button.draw()
            arrow: ArrowButton
            for arrow in arrow_buttons[i]:
                arrow.draw()

        allocated: int | Literal[0] = sum(allocations)
        remaining: int = max(TOTAL_ITEMS - allocated, 0)
        draw_text(f"Allocated: {allocated}, Remaining: {remaining}", GREEN if allocated == TOTAL_ITEMS else RED,
                  WIDTH // 2, 440, centered=True)

        confirm_button.color = GREEN if allocated == TOTAL_ITEMS else GRAY
        confirm_button.draw()

        flip()
        clock.tick(60)


def log_allocation_result(allocations: list[int]) -> None:
    """
    Log the allocation results to a file.

    Args:
        allocations (List[int]): The final allocations to log.
    """
    file: TextIO
    with open(LOG_FILE, 'a') as file:
        file.write(f"Level {level}: {allocations}\n")


def main_game_loop() -> None:
    """
    The main game loop.
    """
    global level
    running: bool = True

    while running:
        event: Event
        for event in get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN and event.key == K_SPACE:
                level += 1
                if level % 2 == 0:
                    result: list[int] | None = allocation_quest()
                    if result is None:
                        running = False
                    else:
                        print(f"Allocation result: {result}")

        screen.fill(WHITE)
        draw_text(f"Level {level}", BLUE, WIDTH // 2, HEIGHT // 2 - 20, centered=True)
        draw_text("Press Space to start allocation quest", BLACK, WIDTH // 2, HEIGHT // 2 + 20, centered=True)

        flip()

    quit()
    exit()


if __name__ == "__main__":
    main_game_loop()
