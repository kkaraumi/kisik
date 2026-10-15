import random

from config import BOARD_SIZE, SHIP_SIZES


class Board:
    def __init__(self):
        self.ships = []
        self.shots = set()
        self.place_ships_randomly()

    def place_ships_randomly(self):
        self.ships = []
        self.shots = set()
        for size in SHIP_SIZES:
            self.ships.append(self.make_free_ship(size))

    def make_free_ship(self, size):
        while True:
            ship = make_random_ship(size)
            if not self.overlaps(ship):
                return ship

    def overlaps(self, ship):
        taken = self.ship_cells()
        return any(cell in taken for cell in ship)

    def ship_cells(self):
        return {cell for ship in self.ships for cell in ship}

    def has_ship(self, x, y):
        return self.find_ship(x, y) is not None

    def was_shot(self, x, y):
        return (x, y) in self.shots

    def find_ship(self, x, y):
        for ship in self.ships:
            if (x, y) in ship:
                return ship
        return None

    def receive_shot(self, x, y):
        if self.was_shot(x, y):
            return "miss"
        self.shots.add((x, y))
        ship = self.find_ship(x, y)
        if ship is None:
            return "miss"
        if self.is_sunk(ship):
            return "sunk"
        return "hit"

    def is_sunk(self, ship):
        return all(cell in self.shots for cell in ship)

    def all_sunk(self):
        return all(self.is_sunk(ship) for ship in self.ships)


def make_random_ship(size):
    if random.choice([True, False]):
        x = random.randint(0, BOARD_SIZE - size)
        y = random.randint(0, BOARD_SIZE - 1)
        return [(x + i, y) for i in range(size)]
    x = random.randint(0, BOARD_SIZE - 1)
    y = random.randint(0, BOARD_SIZE - size)
    return [(x, y + i) for i in range(size)]
