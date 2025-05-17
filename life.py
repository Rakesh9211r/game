import argparse
import random
import time
import pygame
import sys
from typing import Set, Tuple, List

def parse_args():
    parser = argparse.ArgumentParser(description="Conway's Game of Life")
    parser.add_argument('--width', type=int, default=60, help='Width of the grid')
    parser.add_argument('--height', type=int, default=30, help='Height of the grid')
    parser.add_argument('--fps', type=int, default=10, help='Frames per second')
    parser.add_argument('--cell_size', type=int, default=20, help='Size of each cell in pixels')
    return parser.parse_args()

class GameOfLife:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.live_cells: Set[Tuple[int, int]] = set()
        self.generation = 0
        self.paused = True
    
    def initialize_random(self, density: float = 0.2):
        """Initialize the grid with random live cells"""
        self.live_cells = set()
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < density:
                    self.live_cells.add((x, y))
    
    def clear(self):
        """Clear all live cells"""
        self.live_cells = set()
        self.generation = 0
    
    def count_live_neighbors(self, x: int, y: int) -> int:
        """Count the number of live neighbors for a cell"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the cell itself
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) in self.live_cells:
                        count += 1
        return count
    
    def next_generation(self):
        """Calculate the next generation of cells"""
        new_live_cells = set()
        
        # Consider all cells that are currently live or adjacent to live cells
        candidates = set()
        for (x, y) in self.live_cells:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        candidates.add((nx, ny))
        
        for (x, y) in candidates:
            live_neighbors = self.count_live_neighbors(x, y)
            
            # Apply Conway's rules
            if (x, y) in self.live_cells and live_neighbors in [2, 3]:
                new_live_cells.add((x, y))
            elif (x, y) not in self.live_cells and live_neighbors == 3:
                new_live_cells.add((x, y))
        
        self.live_cells = new_live_cells
        self.generation += 1
    
    def toggle_cell(self, x: int, y: int):
        """Toggle a cell between live and dead"""
        if (x, y) in self.live_cells:
            self.live_cells.remove((x, y))
        else:
            self.live_cells.add((x, y))
    
    def save_pattern(self, filename: str):
        """Save the current pattern to a file"""
        with open(filename, 'w') as f:
            for (x, y) in sorted(self.live_cells):
                f.write(f"{x},{y}\n")
    
    def load_pattern(self, filename: str):
        """Load a pattern from a file"""
        self.clear()
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        x, y = map(int, line.split(','))
                        if 0 <= x < self.width and 0 <= y < self.height:
                            self.live_cells.add((x, y))
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with empty grid.")

def main():
    args = parse_args()
    
    # Initialize Pygame
    pygame.init()
    cell_size = args.cell_size
    screen_width = args.width * cell_size + 200  # Extra space for UI
    screen_height = args.height * cell_size
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Conway's Game of Life")
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 16)
    
    # Initialize the game
    game = GameOfLife(args.width, args.height)
    
    # Main game loop
    running = True
    dragging = False
    drawing_live = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.paused = not game.paused
                elif event.key == pygame.K_n and game.paused:
                    game.next_generation()
                elif event.key == pygame.K_c:
                    game.clear()
                elif event.key == pygame.K_r:
                    game.initialize_random()
                elif event.key == pygame.K_s:
                    game.save_pattern('patterns.txt')
                elif event.key == pygame.K_l:
                    game.load_pattern('patterns.txt')
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos[0] // cell_size, event.pos[1] // cell_size
                    if x < args.width:  # Only if clicking in the grid area
                        dragging = True
                        drawing_live = (x, y) not in game.live_cells
                        game.toggle_cell(x, y)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            
            elif event.type == pygame.MOUSEMOTION and dragging:
                x, y = event.pos[0] // cell_size, event.pos[1] // cell_size
                if x < args.width:  # Only if dragging in the grid area
                    if ((x, y) in game.live_cells) != drawing_live:
                        game.toggle_cell(x, y)
        
        # Update game state if not paused
        if not game.paused:
            game.next_generation()
        
        # Draw everything
        screen.fill((240, 240, 240))  # Light gray background
        
        # Draw grid lines
        for x in range(args.width + 1):
            pygame.draw.line(screen, (200, 200, 200), 
                            (x * cell_size, 0), 
                            (x * cell_size, args.height * cell_size))
        for y in range(args.height + 1):
            pygame.draw.line(screen, (200, 200, 200), 
                            (0, y * cell_size), 
                            (args.width * cell_size, y * cell_size))
        
        # Draw live cells
        for (x, y) in game.live_cells:
            pygame.draw.rect(screen, (50, 150, 50), 
                            (x * cell_size + 1, y * cell_size + 1, 
                             cell_size - 1, cell_size - 1))
        
        # Draw UI panel
        panel_x = args.width * cell_size + 10
        pygame.draw.rect(screen, (220, 220, 220), 
                        (panel_x, 0, screen_width - panel_x, screen_height))
        
        # Draw UI text
        status = "Paused" if game.paused else "Running"
        texts = [
            f"Generation: {game.generation}",
            f"Status: {status}",
            f"Live cells: {len(game.live_cells)}",
            f"FPS: {args.fps}",
            "",
            "Controls:",
            "Space: Play/Pause",
            "N: Next generation",
            "C: Clear",
            "R: Random fill",
            "S: Save pattern",
            "L: Load pattern",
            "",
            "Click/drag: Toggle cells"
        ]
        
        for i, text in enumerate(texts):
            text_surface = font.render(text, True, (0, 0, 0))
            screen.blit(text_surface, (panel_x + 10, 10 + i * 20))
        
        pygame.display.flip()
        clock.tick(args.fps)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()