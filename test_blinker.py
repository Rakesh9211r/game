# tests/test_blinker.py
import unittest
from life import GameOfLife

class TestBlinker(unittest.TestCase):
    def test_blinker(self):
        game = GameOfLife(5, 5)
        # Horizontal blinker in the middle
        game.live_cells = {(1, 2), (2, 2), (3, 2)}
        
        # After one generation, should be vertical
        game.next_generation()
        expected = {(2, 1), (2, 2), (2, 3)}
        self.assertEqual(game.live_cells, expected)
        
        # After another generation, should be back to horizontal
        game.next_generation()
        expected = {(1, 2), (2, 2), (3, 2)}
        self.assertEqual(game.live_cells, expected)

if __name__ == "__main__":
    unittest.main()