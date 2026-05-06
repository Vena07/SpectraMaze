import pygame
from .base_block import BaseBlock

class Mixer(BaseBlock):
    def __init__(self, x, y, output_dir, size=100):
        super().__init__(x, y, size)
        self.output_dir = output_dir
        self.colors_in = []

    def on_click(self):
        self.output_dir = (self.output_dir + 1) % 4

    def reset(self):
        self.colors_in = []

    def draw(self, surface):
        super().draw(surface)
        
        # Tech základna
        bg_rect = self.rect.inflate(-20, -20)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 60, 80), bg_rect, 2, border_radius=12)
        
        center = self.rect.center
        
        # Výstupní masivní kanón
        barrel_len = self.size // 2 - 5
        b_w = 14
        if self.output_dir == 0:   b_rect = pygame.Rect(center[0] - b_w//2, center[1] - barrel_len, b_w, barrel_len - 15)
        elif self.output_dir == 1: b_rect = pygame.Rect(center[0] + 15, center[1] - b_w//2, barrel_len - 15, b_w)
        elif self.output_dir == 2: b_rect = pygame.Rect(center[0] - b_w//2, center[1] + 15, b_w, barrel_len - 15)
        elif self.output_dir == 3: b_rect = pygame.Rect(center[0] - barrel_len, center[1] - b_w//2, barrel_len - 15, b_w)
        
        pygame.draw.rect(surface, (80, 80, 100), b_rect, border_radius=4)
        pygame.draw.rect(surface, (200, 200, 200), b_rect, 2, border_radius=4)

    def draw_overlay(self, surface):
        center = self.rect.center
        # Jádo mixéru se vykreslí PŘES lasery, takže pod něj fyzicky zalezou
        pygame.draw.circle(surface, (40, 40, 50), center, self.size // 3)
        pygame.draw.circle(surface, (100, 100, 120), center, self.size // 3, 3)
        
        if len(self.colors_in) > 0:
            mix_r = min(255, sum([c[0] for c in self.colors_in]))
            mix_g = min(255, sum([c[1] for c in self.colors_in]))
            mix_b = min(255, sum([c[2] for c in self.colors_in]))
            pygame.draw.circle(surface, (mix_r, mix_g, mix_b), center, self.size // 4)
        else:
            pygame.draw.circle(surface, (20, 20, 25), center, self.size // 4)

    def interact_with_beam(self, beam_dir, color):
        self.colors_in.append(color)
        # Jakmile získá 2 paprsky, sečte jejich RGB hodnoty
        if len(self.colors_in) == 2:
            c1, c2 = self.colors_in[0], self.colors_in[1]
            r = min(255, c1[0] + c2[0])
            g = min(255, c1[1] + c2[1])
            b = min(255, c1[2] + c2[2])
            return (self.output_dir, (r, g, b)) # Vrací rovnou novou smíchanou barvu!
        
        return None # První paprsek se v mixéru vždy pohltí a čeká na další