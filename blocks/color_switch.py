import pygame
from .base_block import BaseBlock

class ColorSwitch(BaseBlock):
    def __init__(self, x, y, new_color, size=100):
        super().__init__(x, y, size)
        self.new_color = new_color

    def draw(self, surface):
        super().draw(surface)
        
        # Tech základna portálu
        bg_rect = self.rect.inflate(-20, -20)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 60, 80), bg_rect, 2, border_radius=12)
        
        center = self.rect.center
        gate_rect = self.rect.inflate(-40, -40)
        
        # Brána na změnu barvy
        pygame.draw.rect(surface, (20, 20, 25), gate_rect, border_radius=8)
        pygame.draw.rect(surface, self.new_color, gate_rect, 4, border_radius=8)
        
        pygame.draw.circle(surface, self.new_color, center, 15)
        pygame.draw.circle(surface, (255, 255, 255), center, 5)
        
        # Silové vodiče
        pygame.draw.line(surface, self.new_color, (center[0], bg_rect.top), (center[0], gate_rect.top), 4)
        pygame.draw.line(surface, self.new_color, (center[0], gate_rect.bottom), (center[0], bg_rect.bottom), 4)
        pygame.draw.line(surface, self.new_color, (bg_rect.left, center[1]), (gate_rect.left, center[1]), 4)
        pygame.draw.line(surface, self.new_color, (gate_rect.right, center[1]), (bg_rect.right, center[1]), 4)

    def interact_with_beam(self, beam_dir, color):
        # Změní barvu a propustí paprsek dál
        return (beam_dir, self.new_color)