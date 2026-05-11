import pygame
import math
import random

class LaserEngine:
    def __init__(self, block_size=100):
        self.block_size = block_size
        self.beams = []
        self.show_lasers = False
        self.laser_style = "Neon"
        self.is_animating = False
        self.anim_frame = 0
        self.is_exploded = False
        self.explosion_pos = None
        self.explosion_dist = 0
        self.bulb_lit_dist = {}
        self.particles = []
        self.sound_queue = []
        self.last_anim_dist = -1
        self.button_hit_dist = {}
        self.beam_end_dists = []
        self.explosion_particles_generated = False

    def calculate_beams(self, blocks, grid_w=8, grid_h=8):
        changed = True
        iterations = 0
        
        # Pokud paprsek aktivuje tlačítko a to otevře dveře, musíme 
        # paprsky přepočítat, aby mohly dveřmi proletět.
        while changed and iterations < 5:
            changed = False
            iterations += 1
            self.beams = []
            self.is_exploded = False
            self.explosion_particles_generated = False
            self.explosion_pos = None
            self.explosion_dist = 0
            self.bulb_lit_dist = {}
            self.particles = []
            self.sound_queue = []
            self.last_anim_dist = -1
            self.button_hit_dist = {}
            self.beam_end_dists = []
            empty_occupied = {}
            
            for b in blocks:
                if type(b).__name__ == "Bulb": b.is_lit = False
                if type(b).__name__ == "Button": b.is_pressed = False
                if hasattr(b, 'reset') and type(b).__name__ != "Door": b.reset()

            crystals = [b for b in blocks if type(b).__name__ == "Crystal"]
            dx = [0, 1, 0, -1]
            dy = [-1, 0, 1, 0]
            visited = set()
            # Uložení počátku krystalu (is_start = True)
            queue = [(c.x, c.y, c.direction, c.color, 0, True) for c in crystals]

            while queue:
                item = queue.pop(0)
                cx, cy, direction, color, dist = item[:5]
                is_start = item[5] if len(item) > 5 else False
                
                while True:
                    state = (cx, cy, direction)
                    if state in visited: break
                    visited.add(state)

                    nx, ny = cx + dx[direction], cy + dy[direction]
                    
                    # Offset pouze pokud laser startuje z krystalu
                    offset_x = dx[direction] * (self.block_size // 2 - 15) if is_start else 0
                    offset_y = dy[direction] * (self.block_size // 2 - 15) if is_start else 0
                    start_px = (cx * self.block_size + self.block_size // 2 + offset_x, cy * self.block_size + self.block_size // 2 + offset_y)
                    end_px = (nx * self.block_size + self.block_size // 2, ny * self.block_size + self.block_size // 2)
                    
                    if nx < 0 or nx >= grid_w or ny < 0 or ny >= grid_h:
                        self.beams.append((start_px, end_px, color, dist))
                        self.beam_end_dists.append(dist + 1)
                        break 

                    target_block = next((b for b in blocks if b.x == nx and b.y == ny), None)
                    if target_block:
                        result = target_block.interact_with_beam(direction, color)
                        
                        # Zastavení paprsku přesně na okraji bloku (náraz do Zdi nebo zavřených Dveří)
                        if result is None and type(target_block).__name__ in ["Wall", "Door"]:
                            end_px = (nx * self.block_size + self.block_size // 2 - dx[direction] * (self.block_size // 2), 
                                      ny * self.block_size + self.block_size // 2 - dy[direction] * (self.block_size // 2))
                            
                        self.beams.append((start_px, end_px, color, dist))
                        
                        if result == "EXPLOSION":
                            self.is_exploded = True
                            self.explosion_pos = end_px
                            self.explosion_dist = dist + 1
                            queue = [] # Vyčistíme frontu, exploze zastaví veškerý výpočet
                            break
                            
                        # Vizuální oddálení rozsvícení žárovky
                        if type(target_block).__name__ == "Bulb":
                            if getattr(target_block, 'is_lit', False):
                                target_block.is_lit = False
                                self.bulb_lit_dist[target_block] = dist + 1
                            
                        if type(target_block).__name__ == "Button":
                            self.button_hit_dist[target_block] = dist + 1
                            
                        if result is None: 
                            self.beam_end_dists.append(dist + 1)
                            break
                        
                        if not isinstance(result, list): result = [result]
                            
                        for res in result:
                            if isinstance(res, tuple):
                                if len(res) == 5 and res[0] == "TELEPORT":
                                    queue.append((res[1], res[2], res[3], res[4], dist + 1, False))
                                else:
                                    queue.append((nx, ny, res[0], res[1], dist + 1, False))
                            else:
                                if res is not None:
                                    queue.append((nx, ny, res, color, dist + 1, False))
                        break
                    else:
                        self.beams.append((start_px, end_px, color, dist))
                        is_start = False # Po prvním prázdném poli to už není začátek od krystalu
                        # Pokud se do prázdného políčka snaží narvat více paprsků -> Exploze (kromě křižovatky, ta je target_block)
                        if (nx, ny) in empty_occupied:
                            self.is_exploded = True
                            self.explosion_pos = end_px
                            self.explosion_dist = dist + 1
                            queue = []
                            break
                        empty_occupied[(nx, ny)] = True
                        cx, cy = nx, ny
                        dist += 1

            # Kontrola dveří na konci smyčky - změnilo nějaké tlačítko stav?
            door_states = {}
            for b in blocks:
                if type(b).__name__ == "Button":
                    door_states[b.link_id] = door_states.get(b.link_id, False) or b.is_pressed

            for b in blocks:
                if type(b).__name__ == "Door":
                    if b.id in door_states:
                        if b.is_open != door_states[b.id]:
                            b.is_open = door_states[b.id]
                            changed = True

    def update_animation(self):
        # Aktualizace poletujících jisker (částic)
        for p in self.particles[:]:
            p[0] += p[2] # Přičteme rychlost X
            p[1] += p[3] # Přičteme rychlost Y
            p[4] -= 1    # Snížíme životnost
            if p[4] <= 0:
                self.particles.remove(p)
                
        # Generování nových jisker na koncových bodech paprsku
        if self.show_lasers and not self.is_exploded:
            start_points = set(b[0] for b in self.beams)
            for start, end, color, dist in self.beams:
                # Pokud paprsek v tomto bodě končí (nepokračuje z něj další)
                if end not in start_points:
                    is_current_tip = self.is_animating and dist <= self.anim_frame < dist + 1
                    is_finished = not self.is_animating or self.anim_frame >= dist + 1
                    
                    if is_current_tip or is_finished:
                        if is_current_tip:
                            progress = min(1.0, self.anim_frame - dist)
                            cx = start[0] + (end[0] - start[0]) * progress
                            cy = start[1] + (end[1] - start[1]) * progress
                        else:
                            cx, cy = end
                            
                        # Vytváříme 1-2 jiskry každou sekundu pro cool efekt hoření
                        for _ in range(2 if is_current_tip else 1):
                            if random.random() < (0.6 if is_current_tip else 0.15):
                                vx = random.uniform(-2, 2)
                                vy = random.uniform(-2, 2)
                                life = random.randint(10, 25)
                                self.particles.append([cx, cy, vx, vy, life, color])

        if self.is_animating:
            self.anim_frame += 0.5
            
            # Kontrola událostí a vložení zvuků do fronty podle aktuální vzdálenosti paprsku
            current_dist = int(self.anim_frame)
            if current_dist > self.last_anim_dist:
                if current_dist in self.bulb_lit_dist.values():
                    self.sound_queue.append("bulb")
                if current_dist in self.button_hit_dist.values():
                    self.sound_queue.append("door")
                if current_dist in self.beam_end_dists:
                    self.sound_queue.append("hit")
                self.last_anim_dist = current_dist
            
            # Rozsvícení žárovek až když paprsek fyzicky doletí
            for b, d in self.bulb_lit_dist.items():
                if self.anim_frame >= d:
                    b.is_lit = True
                else:
                    b.is_lit = False
            
            max_dist = max([b[3] for b in self.beams]) if self.beams else 0
            
            if self.is_exploded:
                if self.anim_frame >= self.explosion_dist:
                    # Vygenerování masivní prskající exploze při srážce
                    if not self.explosion_particles_generated:
                        for _ in range(60):
                            vx = random.uniform(-8, 8)
                            vy = random.uniform(-8, 8)
                            life = random.randint(20, 60)
                            color = random.choice([(255, 50, 0), (255, 150, 0), (255, 255, 0), (255, 255, 255)])
                            self.particles.append([self.explosion_pos[0], self.explosion_pos[1], vx, vy, life, color])
                        self.explosion_particles_generated = True
                        
                    self.is_animating = False
            elif self.anim_frame >= max_dist + 1:
                self.is_animating = False

    def draw(self, surface):
        if not self.show_lasers: return

        time_ms = pygame.time.get_ticks()
        pulse = (math.sin(time_ms / 100.0) + 1) / 2.0 # Rychlejší a agresivnější pulzování
        
        # 1. Krok: Výpočet aktuálních pozic všech segmentů (kvůli animaci)
        active_segments = []
        for start, end, color, dist in self.beams:
            if self.is_animating:
                if dist > self.anim_frame: continue
                progress = min(1.0, self.anim_frame - dist)
                cur_end = (start[0] + (end[0] - start[0]) * progress, start[1] + (end[1] - start[1]) * progress)
            else:
                cur_end = end
            active_segments.append((start, cur_end, color))
            
        # 2. Krok: Vykreslení ve vrstvách (Painter's algorithm)
        # Nejdřív stíny, pak záře, nakonec bílé středy. Tím se celý paprsek vizuálně spojí.
        glow_w = int(pulse * 6)

        for layer_idx in range(5):
            for start, cur_end, color in active_segments:
                r, g, b_col = color
                width = 0
                l_color = (0, 0, 0)
                
                if self.laser_style == "Plasma":
                    wobble = int((math.sin(time_ms / 40.0) + 1) * 4)
                    if layer_idx == 0: width, l_color = 18, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 14 + wobble, (int(r*0.3), int(g*0.3), int(b_col*0.3))
                    elif layer_idx == 2: width, l_color = 10 + wobble//2, (int(r*0.7), int(g*0.7), int(b_col*0.7))
                    elif layer_idx == 3: width, l_color = 6, color
                    elif layer_idx == 4: width, l_color = 3, (min(255, r+100), min(255, g+100), min(255, b_col+100))
                elif self.laser_style == "Focused":
                    if layer_idx == 0: width, l_color = 10, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 6, (int(r*0.4), int(g*0.4), int(b_col*0.4))
                    elif layer_idx == 2: width, l_color = 3, color
                    elif layer_idx == 3: width, l_color = 1, (255, 255, 255)
                elif self.laser_style == "Helix":
                    if layer_idx == 0: width, l_color = 12, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 8 + glow_w//2, (int(r*0.3), int(g*0.3), int(b_col*0.3))
                    elif layer_idx == 2: width, l_color = 4, color
                elif self.laser_style == "Quantum":
                    if layer_idx == 0: width, l_color = 14, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 10 + glow_w, (int(r*0.2), int(g*0.2), int(b_col*0.2))
                    elif layer_idx == 2: width, l_color = 6, color
                    elif layer_idx == 3: width, l_color = 2, (255, 255, 255)
                else: # Neon
                    if layer_idx == 0: width, l_color = 16, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 12 + glow_w, (int(r*0.2), int(g*0.2), int(b_col*0.2))
                    elif layer_idx == 2: width, l_color = 8 + glow_w//2, (int(r*0.6), int(g*0.6), int(b_col*0.6))
                    elif layer_idx == 3: width, l_color = 4, color
                    elif layer_idx == 4: width, l_color = 2, (255, 255, 255)
                    
                if width > 0:
                    pygame.draw.line(surface, l_color, start, cur_end, width)
                    radius = width // 2
                    if radius > 0:
                        pygame.draw.circle(surface, l_color, (int(start[0]), int(start[1])), radius)
                        pygame.draw.circle(surface, l_color, (int(cur_end[0]), int(cur_end[1])), radius)

        # 3. Krok: Vykreslení speciálních geometrických tvarů kolem laserů
        for start, cur_end, color in active_segments:
            length = math.hypot(cur_end[0] - start[0], cur_end[1] - start[1])
            if length == 0: continue
            ux, uy = (cur_end[0] - start[0]) / length, (cur_end[1] - start[1]) / length
            vx, vy = -uy, ux # Kolmý vektor
            
            if self.laser_style == "Helix":
                pts1, pts2 = [], []
                for i in range(0, int(length) + 1, 5):
                    px, py = start[0] + ux * i, start[1] + uy * i
                    t = (px + py) * 0.02 - time_ms / 150.0
                    offset = math.sin(t) * 10
                    pts1.append((px + vx * offset, py + vy * offset))
                    pts2.append((px - vx * offset, py - vy * offset))
                if len(pts1) > 1: pygame.draw.lines(surface, color, False, pts1, 2); pygame.draw.lines(surface, (255, 255, 255), False, pts1, 1)
                if len(pts2) > 1: pygame.draw.lines(surface, color, False, pts2, 2); pygame.draw.lines(surface, (255, 255, 255), False, pts2, 1)
            
            elif self.laser_style == "Quantum":
                offset_val = (time_ms * 0.1) % 20
                for travel in range(int(offset_val), int(length), 20):
                    px, py = start[0] + ux * travel, start[1] + uy * travel
                    t_val = (px + py) * 0.02 + time_ms * 0.005
                    offset = math.sin(t_val) * 12
                    s = 4 + math.sin(t_val * 2) * 3
                    rect = pygame.Rect(px + vx * offset - s/2, py + vy * offset - s/2, s, s)
                    pygame.draw.rect(surface, color, rect)
                    pygame.draw.rect(surface, (255, 255, 255), rect, 1)

            elif self.laser_style == "Plasma":
                if random.random() < 0.5:
                    pts = []
                    for i in range(0, int(length) + 1, 10):
                        offset = random.uniform(-8, 8)
                        pts.append((start[0] + ux * i + vx * offset, start[1] + uy * i + vy * offset))
                    if len(pts) > 1: pygame.draw.lines(surface, (255, 255, 255), False, pts, 1)

            elif self.laser_style == "Focused":
                offset_val = (time_ms * 0.2) % 25
                for travel in range(int(offset_val), int(length), 25):
                    px, py = start[0] + ux * travel, start[1] + uy * travel
                    pygame.draw.circle(surface, color, (int(px), int(py)), 6, 1)
                    pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 3)

        # Vykreslení částic (jisker) z nárazů laseru
        for p in self.particles:
            x, y, vx, vy, life, color = p
            r, g, b_col = color
            # Čím kratší život částice má, tím více ztrácí bělost a přechází do barvy laseru
            intensity = min(1.0, life / 25.0)
            p_color = (
                min(255, int(r * intensity + 255 * (1 - intensity))),
                min(255, int(g * intensity + 255 * (1 - intensity))),
                min(255, int(b_col * intensity + 255 * (1 - intensity)))
            )
            pygame.draw.circle(surface, p_color, (int(x), int(y)), max(1, life // 6))

        if self.is_exploded and self.explosion_pos:
            if self.anim_frame >= self.explosion_dist:
                # Zlepšený masivní efekt exploze s vrstvami
                pygame.draw.circle(surface, (255, 50, 0), self.explosion_pos, int(50 + pulse * 30), 8)
                pygame.draw.circle(surface, (255, 100, 0), self.explosion_pos, int(30 + pulse * 15), 4)
                pygame.draw.circle(surface, (255, 255, 255), self.explosion_pos, int(10 + pulse * 5))
                pygame.draw.circle(surface, (255, 0, 0), self.explosion_pos, 80, 2)

    def is_victory(self, blocks):
        bulbs = [b for b in blocks if type(b).__name__ == "Bulb"]
        if not bulbs: return False
        # Zkontroluje, zda úplně všechny žárovky v úrovni svítí
        return all(b.is_lit for b in bulbs)