import unittest

from config import BOARD_SIZE, SHIP_SIZES
from game import Board, cells_around, find_connected


def make_board(ships):
    board = Board()
    board.ships = ships
    board.shots = set()
    return board


class BoardTest(unittest.TestCase):
    def test_random_placement_has_twenty_cells(self):
        for _ in range(200):
            board = Board()
            cells = [cell for ship in board.ships for cell in ship]
            self.assertEqual(len(cells), 20)
            self.assertEqual(len(set(cells)), 20)

    def test_random_placement_has_right_ships(self):
        board = Board()
        sizes = sorted(len(ship) for ship in board.ships)
        self.assertEqual(sizes, sorted(SHIP_SIZES))

    def test_ships_are_inside_board_and_straight(self):
        for _ in range(200):
            board = Board()
            for ship in board.ships:
                xs = {x for x, y in ship}
                ys = {y for x, y in ship}
                self.assertTrue(len(xs) == 1 or len(ys) == 1)
                self.assertEqual(len(xs) + len(ys) - 1, len(ship))
                for x, y in ship:
                    self.assertTrue(0 <= x < BOARD_SIZE)
                    self.assertTrue(0 <= y < BOARD_SIZE)

    def test_ships_do_not_touch(self):
        for _ in range(200):
            board = Board()
            for ship in board.ships:
                others = {cell for other in board.ships if other is not ship for cell in other}
                for x, y in ship:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            self.assertNotIn((x + dx, y + dy), others)

    def test_place_again_clears_shots(self):
        board = Board()
        board.receive_shot(0, 0)
        board.place_ships_randomly()
        self.assertEqual(board.shots, set())
        self.assertEqual(len(board.ship_cells()), 20)

    def test_miss(self):
        board = make_board([[(0, 0), (1, 0)]])
        self.assertEqual(board.receive_shot(5, 5), "miss")

    def test_hit_and_sunk(self):
        board = make_board([[(0, 0), (1, 0)], [(5, 5)]])
        self.assertEqual(board.receive_shot(0, 0), "hit")
        self.assertEqual(board.receive_shot(1, 0), "sunk")
        self.assertFalse(board.all_sunk())

    def test_single_cell_ship_is_sunk_at_once(self):
        board = make_board([[(3, 4)]])
        self.assertEqual(board.receive_shot(3, 4), "sunk")

    def test_win_when_all_ships_sunk(self):
        board = make_board([[(0, 0), (0, 1)], [(9, 9)]])
        board.receive_shot(0, 0)
        board.receive_shot(0, 1)
        self.assertFalse(board.all_sunk())
        board.receive_shot(9, 9)
        self.assertTrue(board.all_sunk())

    def test_full_board_win(self):
        board = Board()
        for x, y in board.ship_cells():
            self.assertIn(board.receive_shot(x, y), ["hit", "sunk"])
        self.assertTrue(board.all_sunk())

    def test_repeated_shot(self):
        board = make_board([[(0, 0), (1, 0)]])
        self.assertEqual(board.receive_shot(0, 0), "hit")
        self.assertTrue(board.was_shot(0, 0))
        self.assertEqual(board.receive_shot(0, 0), "miss")
        self.assertEqual(len(board.shots), 1)


class SunkShipTest(unittest.TestCase):
    def test_cells_around_ship_in_middle(self):
        around = cells_around([(4, 4), (5, 4)])
        self.assertEqual(len(around), 10)
        self.assertIn((3, 3), around)
        self.assertIn((6, 5), around)
        self.assertNotIn((4, 4), around)

    def test_cells_around_ship_in_corner(self):
        around = cells_around([(0, 0)])
        self.assertEqual(around, {(1, 0), (0, 1), (1, 1)})

    def test_find_connected_takes_only_one_ship(self):
        hits = {(2, 2), (3, 2), (4, 2), (7, 7)}
        self.assertEqual(find_connected(hits, (3, 2)), {(2, 2), (3, 2), (4, 2)})
        self.assertEqual(find_connected(hits, (7, 7)), {(7, 7)})

    def test_find_connected_ignores_diagonal(self):
        hits = {(1, 1), (2, 2)}
        self.assertEqual(find_connected(hits, (1, 1)), {(1, 1)})

    def test_sunk_cells(self):
        board = make_board([[(0, 0), (1, 0)], [(5, 5)]])
        board.receive_shot(0, 0)
        self.assertEqual(board.sunk_cells(), set())
        board.receive_shot(1, 0)
        self.assertEqual(board.sunk_cells(), {(0, 0), (1, 0)})


if __name__ == "__main__":
    unittest.main()
