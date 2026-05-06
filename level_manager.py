import requests
import random
import json
from blocks.crystal import Crystal
from blocks.bulb import Bulb
from blocks.mirror import Mirror
from blocks.mixer import Mixer
from blocks.crossover import Crossover
from blocks.color_switch import ColorSwitch
from blocks.splitter import Splitter
from blocks.button import Button
from blocks.door import Door
from blocks.teleporter import Teleporter
from blocks.block import Wall

class LevelManager:
    def __init__(self, screen_w=900, screen_h=900):
        self.screen_w = screen_w
        self.screen_h = screen_h
        # Původní velikost 100px (opravuje vycentrování laseru z enginu)
        self.block_size = 100
        self.grid_w = 8
        self.grid_h = 8
        
        # URL adresa tvého webu (API)
        # self.api_url = "http://localhost:3000/api/maps" # Pro testování u tebe na PC (musíš mít zapnutý web)
        self.api_url = "https://spectra-maze-web.vercel.app/api/maps" # Pro finální verzi po nahrání na Vercel
        
        # Slovník s pískovišti pro všechny bloky
        self.block_tutorials = {
            "Crystal": {
                "title": "Krystal (Zdroj)",
                "desc": "Základní zdroj energie. Kliknutím levým tlačítkem myši krystal otočíš o 90 stupňů.",
                "level": [{"type": "Crystal", "x": 0, "y": 2, "dir": 1, "color": (255, 0, 0)}, {"type": "Bulb", "x": 3, "y": 2, "color": (255, 0, 0)}]
            },
            "Bulb": {
                "title": "Žárovka (Cíl)",
                "desc": "Tvá meta. Musíš do ní přivést paprsek energie o přesně shodné barvě.",
                "level": [{"type": "Crystal", "x": 0, "y": 2, "dir": 1, "color": (0, 255, 0)}, {"type": "Bulb", "x": 3, "y": 2, "color": (0, 255, 0)}]
            },
            "Mirror": {
                "title": "Zrcadlo",
                "desc": "Odráží paprsek o 90 stupňů. Kliknutím překlopíš jeho orientaci.",
                "level": [{"type": "Crystal", "x": 0, "y": 3, "dir": 0, "color": (0, 0, 255)}, {"type": "Mirror", "x": 0, "y": 0, "orientation": 1}, {"type": "Bulb", "x": 3, "y": 0, "color": (0, 0, 255)}]
            },
            "Splitter": {
                "title": "Rozdvojník",
                "desc": "Rozdělí paprsek do dvou směrů kolmo na směr letu. Kliknutím změníš osu.",
                "level": [{"type": "Crystal", "x": 2, "y": 3, "dir": 0, "color": (255, 255, 0)}, {"type": "Splitter", "x": 2, "y": 1, "orientation": 1}, {"type": "Bulb", "x": 0, "y": 1, "color": (255, 255, 0)}, {"type": "Bulb", "x": 3, "y": 1, "color": (255, 255, 0)}]
            },
            "ColorSwitch": {
                "title": "Měnič barev",
                "desc": "Přebarví procházející paprsek na svou vlastní barvu.",
                "level": [{"type": "Crystal", "x": 0, "y": 2, "dir": 1, "color": (255, 0, 0)}, {"type": "ColorSwitch", "x": 1, "y": 2, "color": (0, 255, 0)}, {"type": "Bulb", "x": 3, "y": 2, "color": (0, 255, 0)}]
            },
            "Mixer": {
                "title": "Mixér barev",
                "desc": "Spojí 2 paprsky do jedné barvy (červená+zelená=žlutá). Kliknutím otočíš výstup.",
                "level": [{"type": "Crystal", "x": 2, "y": 0, "dir": 2, "color": (255, 0, 0)}, {"type": "Crystal", "x": 0, "y": 2, "dir": 1, "color": (0, 255, 0)}, {"type": "Mixer", "x": 2, "y": 2, "output_dir": 2}, {"type": "Bulb", "x": 2, "y": 3, "color": (255, 255, 0)}]
            },
            "Crossover": {
                "title": "Křižovatka",
                "desc": "Umožní dvěma paprskům se bezpečně překřížit bez smíchání a bez exploze.",
                "level": [{"type": "Crystal", "x": 2, "y": 0, "dir": 2, "color": (255, 0, 0)}, {"type": "Crystal", "x": 0, "y": 2, "dir": 1, "color": (0, 0, 255)}, {"type": "Crossover", "x": 2, "y": 2}, {"type": "Bulb", "x": 2, "y": 3, "color": (255, 0, 0)}, {"type": "Bulb", "x": 3, "y": 2, "color": (0, 0, 255)}]
            },
            "ButtonDoor": {
                "title": "Tlačítko a Dveře",
                "desc": "Zasáhni tlačítko laserem pro odemčení všech dveří se stejným číslem.",
                "level": [{"type": "Crystal", "x": 0, "y": 0, "dir": 1, "color": (0, 255, 0)}, {"type": "Button", "x": 1, "y": 0, "link_id": 1}, {"type": "Mirror", "x": 3, "y": 0, "orientation": 1}, {"type": "Door", "x": 3, "y": 2, "id": 1}, {"type": "Bulb", "x": 3, "y": 3, "color": (0, 255, 0)}]
            },
            "Teleporter": {
                "title": "Teleport",
                "desc": "Okamžitě přesune paprsek na jiný teleport se stejným kanálem. Zachovává směr.",
                "level": [{"type": "Crystal", "x": 0, "y": 3, "dir": 1, "color": (255, 0, 255)}, {"type": "Teleporter", "x": 1, "y": 3, "channel": 1}, {"type": "Teleporter", "x": 2, "y": 0, "channel": 1}, {"type": "Bulb", "x": 3, "y": 0, "color": (255, 0, 255)}]
            },
            "Explosion": {
                "title": "Exploze (Chyba)",
                "desc": "Když se dva paprsky srazí čelně v jednom poli, dojde ke katastrofální explozi a hra se zastaví.",
                "level": [{"type": "Crystal", "x": 0, "y": 2, "dir": 1, "color": (255, 0, 0)}, {"type": "Crystal", "x": 3, "y": 2, "dir": 3, "color": (0, 255, 0)}]
            }
        }

    def load_community_level(self, level_id):
        try:
            url = f"{self.api_url}/{level_id}"
            response = requests.get(url, timeout=5)
            response.raise_for_status() # Zkontroluje, zda nedošlo k chybě (např. mapa neexistuje)
            
            print(f"\n=== DEBUG NAČÍTÁNÍ MAPY ID {level_id} ===")
            print(f"1. RAW Odpověď webu: {response.text[:300]}")
            
            # Krok 1: Získání JSONu z odpovědi
            data_from_api = response.json()
            
            # Krok 2: Rozbalení, pokud je odpověď jen text
            while isinstance(data_from_api, str):
                data_from_api = json.loads(data_from_api)
            
            print(f"2. Po rozbalení je hlavní objekt typu: {type(data_from_api)}")

            # Krok 3: Nalezení skutečných dat mapy uvnitř objektu
            # API může vrátit celý řádek z databáze: {"id": ..., "title": ..., "levelData": "{...}"}
            # Nebo může vrátit už přímo objekt mapy: {"size": 6, "blocks": [...]}
            map_object = None
            if isinstance(data_from_api, dict):
                if "blocks" in data_from_api:
                    # Případ A: API vrátilo přímo objekt mapy
                    map_object = data_from_api
                    print("3. Nalezeno: API vrátilo přímo objekt mapy.")
                else:
                    # Případ B: API vrátilo řádek z databáze, hledáme data v jeho sloupcích
                    print(f"3. Hledám data mapy ve sloupcích: {list(data_from_api.keys())}")
                    # Hledáme klíč, který se jmenuje 'levelData' (nebo podobně)
                    for key, value in data_from_api.items():
                        if 'data' in key.lower() or 'level' in key.lower():
                            potential_map_data = value
                            # Opakovaně rozbalujeme, pokud je to vnořený text
                            while isinstance(potential_map_data, str):
                                try:
                                    potential_map_data = json.loads(potential_map_data)
                                except json.JSONDecodeError:
                                    break # Pokud to není platný JSON, končíme
                            
                            if isinstance(potential_map_data, dict) and "blocks" in potential_map_data:
                                map_object = potential_map_data
                                print(f"4. ÚSPĚCH! Data mapy nalezena ve sloupci '{key}'.")
                                break
            
            if map_object is None:
                print("CHYBA: Nepodařilo se najít platný objekt mapy s klíčem 'blocks'.")
                return []

            # Krok 4: Zpracování nalezených dat
            self.grid_w = int(map_object.get("size", 8))
            self.grid_h = int(map_object.get("size", 8))
            print(f"5. Mřížka hry nastavena na: {self.grid_w}x{self.grid_h}")
            
            blocks_list = map_object.get("blocks", [])
            print(f"6. Počet bloků k vykreslení: {len(blocks_list)}")

            # Krok 5: Vytvoření bloků ve hře
            final_blocks = self._build_blocks_from_data(blocks_list)
            print(f"7. ÚSPĚŠNĚ VYTVOŘENO {len(final_blocks)} BLOKŮ!")
            print(f"=======================================\n")
            return final_blocks
        except Exception as e:
            print(f"\n--- CHYBA NAČÍTÁNÍ MAPY ID {level_id} ---")
            print(f"Chyba: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Odpověď webu: {e.response.text[:300]}")
            print(f"-----------------------------------\n")
            return []

    def search_community_levels(self, query=""):
        try:
            url = f"{self.api_url}?search={query}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            # Pokud web vrací objekt např. {"maps": [...]}, vytáhneme z něj rovnou seznam
            if isinstance(data, dict):
                data = data.get("maps", data.get("data", []))
                
            return data
        except Exception as e:
            print(f"\n--- CHYBA NAČÍTÁNÍ SEZNAMU MAP ---")
            print(f"URL: {self.api_url}")
            print(f"Chyba: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Odpověď webu: {e.response.text[:300]}")
            print(f"-----------------------------------\n")
            return []

    def rate_map(self, level_id, rating):
        # TATO FUNKCE JE PŘIPRAVENA PRO BUDOUCNOST
        # Zde by se odeslal požadavek na tvé API, např. POST na /api/maps/{level_id}/rate
        # Je potřeba poslat i autorizační token přihlášeného uživatele.
        print(f"Odesílám na server: mapa {level_id} dostala hodnocení {rating}.")

    def generate_ai_level(self, difficulty):
            # Konfigurace obtížnosti s dynamickou velikostí mapy
            configs = {
                "easy":   {"grid": [5, 6], "paths": 1, "path_len": (5, 7), "special_chance": 0.30, "allowed_specials": ["ColorSwitch", "Splitter", "Button", "Wall"], "min_blocks": 6},
                "medium": {"grid": [6, 7], "paths": random.choice([1, 2]), "path_len": (6, 8), "special_chance": 0.40, "allowed_specials": ["ColorSwitch", "Splitter", "Crossover", "Button", "Teleporter", "Wall"], "min_blocks": 9},
                "hard":   {"grid": [8], "paths": 3, "path_len": (15, 25), "special_chance": 0.85, "allowed_specials": ["ColorSwitch", "Splitter", "Crossover", "Mixer", "Button", "Teleporter"], "min_blocks": 25, "end_chance": 0.05}
            }
            
            config = configs.get(difficulty, configs["medium"])
            grid_size = random.choice(config["grid"])
            self.grid_w = self.grid_h = grid_size

            # Slovník pro snadný pohyb v mřížce (0: Nahoru, 1: Doprava, 2: Dolů, 3: Doleva)
            DIRECTIONS = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}

            def is_free(x, y, grid):
                return 0 <= x < grid_size and 0 <= y < grid_size and (x, y) not in grid

            for attempt in range(1000): # Díky chytřejší logice můžeme snížit počet pokusů
                grid = {} 
                blocks = []
                success = True
                
                pending_paths = []
                buttons_available = []
                teleporters_available = []
                doors_needed = 0

                # 1. Vytvoření startovních krystalů
                for _ in range(config["paths"]):
                    cx, cy = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
                    if (cx, cy) in grid: 
                        success = False
                        break
                    cdir = random.randint(0, 3)
                    color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
                    
                    blocks.append({"type": "Crystal", "x": cx, "y": cy, "dir": cdir, "color": color})
                    grid[(cx, cy)] = 'block'
                    pending_paths.append((cx, cy, cdir, color, random.randint(*config["path_len"])))
                    
                if not success: continue

                # 2. Postupné prodlužování všech cest
                while pending_paths:
                    curr_x, curr_y, curr_dir, color, length_left = pending_paths.pop(0)

                    # Posun vpřed
                    dx, dy = DIRECTIONS[curr_dir]
                    nx, ny = curr_x + dx, curr_y + dy
                    
                    # Pokud narazíme na zeď/blok hned na dalším poli, zkusíme ukončit žárovkou, nebo zrcadlem
                    if not is_free(nx, ny, grid):
                        if length_left <= 0:
                            blocks.append({"type": "Bulb", "x": curr_x, "y": curr_y, "color": color})
                            grid[(curr_x, curr_y)] = 'block'
                        else:
                            success = False # Tady cesta umřela moc brzy
                        break

                    grid[(nx, ny)] = 'laser'
                    length_left -= 1

                    # Kontrola dalšího pole rovně
                    next_x, next_y = nx + dx, ny + dy
                    straight_blocked = not is_free(next_x, next_y, grid)

                    # Ukončení cesty
                    end_chance = config.get("end_chance", 0.4)
                    if length_left <= 0 or (straight_blocked and random.random() < end_chance):
                        blocks.append({"type": "Bulb", "x": nx, "y": ny, "color": color})
                        grid[(nx, ny)] = 'block'
                        continue

                    use_special = random.random() < config["special_chance"] and config["allowed_specials"]
                    placed_special = False

                    if use_special:
                        block_choices = [s for s in config["allowed_specials"] if s != "Wall"]
                        if doors_needed > 0 and (random.random() < 0.6 or length_left <= 2):
                            block_type = "Door"
                        else:
                            if difficulty == "hard" and block_choices:
                                # U těžké obtížnosti agresivně volíme ty nejsložitější bloky pro plný potenciál
                                weights = []
                                for b in block_choices:
                                    if b in ["Mixer", "Teleporter", "Crossover", "Splitter"]: weights.append(4)
                                    elif b == "Button": weights.append(2)
                                    else: weights.append(1)
                                block_type = random.choices(block_choices, weights=weights, k=1)[0]
                            else:
                                block_type = random.choice(block_choices) if block_choices else "Mirror"
                            
                        if straight_blocked and block_type in ["ColorSwitch", "Button", "Door", "Mixer", "Crossover"]:
                            use_special = False
                            
                        if use_special:
                            if block_type == "ColorSwitch":
                                new_color = random.choice([(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)])
                                blocks.append({"type": "ColorSwitch", "x": nx, "y": ny, "color": new_color})
                                pending_paths.append((nx, ny, curr_dir, new_color, length_left))
                                placed_special = True
                                
                            elif block_type == "Splitter":
                                orient = 0 if curr_dir in (1, 3) else 1
                                free_dirs = [d for d in (([0, 2] if orient == 0 else [1, 3])) if is_free(nx + DIRECTIONS[d][0], ny + DIRECTIONS[d][1], grid)]
                                if free_dirs:
                                    blocks.append({"type": "Splitter", "x": nx, "y": ny, "orientation": orient})
                                    for d in free_dirs:
                                        pending_paths.append((nx, ny, d, color, length_left))
                                    placed_special = True
                                
                            elif block_type in ["Crossover", "Mixer"]:
                                cross_dir = random.choice([(curr_dir + 1) % 4, (curr_dir + 3) % 4])
                                cx, cy = nx - DIRECTIONS[cross_dir][0], ny - DIRECTIONS[cross_dir][1]
                                
                                if is_free(cx, cy, grid):
                                    cross_color = random.choice([(255,0,0), (0,255,0), (0,0,255)])
                                    blocks.append({"type": "Crystal", "x": cx, "y": cy, "dir": cross_dir, "color": cross_color})
                                    grid[(cx, cy)] = 'block'
                                    
                                    if block_type == "Crossover":
                                        blocks.append({"type": "Crossover", "x": nx, "y": ny})
                                        pending_paths.append((nx, ny, curr_dir, color, length_left))
                                        pending_paths.append((nx, ny, cross_dir, cross_color, length_left))
                                    else:
                                        mixed_color = (min(255, color[0] + cross_color[0]), min(255, color[1] + cross_color[1]), min(255, color[2] + cross_color[2]))
                                        blocks.append({"type": "Mixer", "x": nx, "y": ny, "output_dir": curr_dir})
                                        pending_paths.append((nx, ny, curr_dir, mixed_color, length_left))
                                    placed_special = True

                            elif block_type == "Button":
                                btn_id = len(buttons_available) + 1
                                blocks.append({"type": "Button", "x": nx, "y": ny, "link_id": btn_id})
                                buttons_available.append(btn_id)
                                doors_needed += 1
                                pending_paths.append((nx, ny, curr_dir, color, length_left))
                                placed_special = True

                            elif block_type == "Door" and buttons_available:
                                blocks.append({"type": "Door", "x": nx, "y": ny, "id": random.choice(buttons_available)})
                                doors_needed -= 1
                                pending_paths.append((nx, ny, curr_dir, color, length_left))
                                placed_special = True
                                
                            elif block_type == "Teleporter":
                                empty_spots = [(rx, ry) for rx in range(grid_size) for ry in range(grid_size) if is_free(rx, ry, grid) and is_free(rx + dx, ry + dy, grid)]
                                if empty_spots:
                                    tx, ty = random.choice(empty_spots)
                                    channel = len(teleporters_available) + 1
                                    blocks.extend([{"type": "Teleporter", "x": nx, "y": ny, "channel": channel}, {"type": "Teleporter", "x": tx, "y": ty, "channel": channel}])
                                    grid[(tx, ty)] = 'block'
                                    teleporters_available.append(channel)
                                    pending_paths.append((tx, ty, curr_dir, color, length_left))
                                    placed_special = True

                            if placed_special:
                                grid[(nx, ny)] = 'block'

                    if not placed_special:
                        # Logika pro zrcadlo
                        valid_turns = [turn for turn in [-1, 1] if is_free(nx + DIRECTIONS[(curr_dir + turn) % 4][0], ny + DIRECTIONS[(curr_dir + turn) % 4][1], grid)]
                        
                        if valid_turns:
                            turn = random.choice(valid_turns)
                            new_dir = (curr_dir + turn) % 4
                            orient = 1 if (curr_dir, new_dir) in [(0, 1), (1, 0), (2, 3), (3, 2)] else 0
                            blocks.append({"type": "Mirror", "x": nx, "y": ny, "orientation": orient})
                            pending_paths.append((nx, ny, new_dir, color, length_left))
                        else:
                            blocks.append({"type": "Bulb", "x": nx, "y": ny, "color": color})
                        grid[(nx, ny)] = 'block'

                if not success or doors_needed > 0 or len(blocks) < config.get("min_blocks", 4): 
                    continue
                        
                if success:
                    # Přidání překážek (Zdí) na konci
                    if "Wall" in config["allowed_specials"]:
                        empty_spaces = [(x, y) for x in range(grid_size) for y in range(grid_size) if (x, y) not in grid]
                        for _ in range(min(random.randint(0, grid_size), len(empty_spaces))):
                            wx, wy = empty_spaces.pop(random.randint(0, len(empty_spaces) - 1))
                            blocks.append({"type": "Wall", "x": wx, "y": wy})
                    
                    # Dodatečná náhodná rotace některých bloků pro zmatení hráče
                    for b in blocks:
                        if b["type"] in ["Crystal", "Mixer"]: b.setdefault("dir", random.randint(0, 3)); b.setdefault("output_dir", random.randint(0, 3))
                        elif b["type"] in ["Mirror", "Splitter"]: b["orientation"] = random.randint(0, 1)
                    return self._build_blocks_from_data(blocks)
                    
            print(f"POZOR: Nepodařilo se vygenerovat mapu (obtížnost {difficulty}), načítám tutoriál.")
            self.grid_w = self.grid_h = 8
            return self.load_tutorial("Crystal")

    def load_tutorial(self, block_name):
        self.grid_w = 4
        self.grid_h = 4
        level_data = self.block_tutorials.get(block_name, {}).get("level", [])
        return self._build_blocks_from_data(level_data)

    def _build_blocks_from_data(self, level_data):
        blocks = []
        doors = {}
        teleporters = {}
        
        # Dynamický výpočet velikosti bloku pro mobilní responzivitu
        max_w = self.screen_w * 0.95
        max_h = self.screen_h - 150 # Rezerva pro UI nahoře a dole
        self.block_size = int(min(100, max_w / max(1, self.grid_w), max_h / max(1, self.grid_h)))
        
        # Pokud editor náhodou uložil pole jako očíslovaný slovník ({"0": {...}})
        if isinstance(level_data, dict):
            level_data = list(level_data.values())
            
        for data in level_data:
            # Pokud je samotný blok uvnitř pole stále string (vícenásobné převedení na webu)
            while isinstance(data, str):
                try: data = json.loads(data)
                except: break
                
            if not isinstance(data, dict):
                continue
                
            # Normalizace názvu typu (např. "color_switch" z webu se přeloží na "colorswitch")
            b_type = data.get("type", "").lower().replace("_", "")
            
            block_obj = None
            if b_type == "crystal":
                block_obj = Crystal(data["x"], data["y"], data.get("dir", 0), data.get("color", [255, 0, 0]), self.block_size)
            elif b_type == "bulb":
                block_obj = Bulb(data["x"], data["y"], data.get("color", [255, 0, 0]), self.block_size)
            elif b_type == "mirror":
                block_obj = Mirror(data["x"], data["y"], data.get("orientation", 0), self.block_size)
            elif b_type == "mixer":
                block_obj = Mixer(data["x"], data["y"], data.get("output_dir", 0), self.block_size)
            elif b_type == "crossover":
                block_obj = Crossover(data["x"], data["y"], self.block_size)
            elif b_type == "colorswitch":
                block_obj = ColorSwitch(data["x"], data["y"], data.get("color", [255, 255, 255]), self.block_size)
            elif b_type == "splitter":
                block_obj = Splitter(data["x"], data["y"], data.get("orientation", 0), self.block_size)
            elif b_type == "door":
                block_obj = Door(data["x"], data["y"], self.block_size)
                block_obj.id = data.get("id", 0)
                if block_obj.id not in doors:
                    doors[block_obj.id] = []
                doors[block_obj.id].append(block_obj)
            elif b_type == "button":
                block_obj = Button(data["x"], data["y"], self.block_size)
                block_obj.link_id = data.get("link_id", 0)
            elif b_type == "teleporter":
                block_obj = Teleporter(data["x"], data["y"], self.block_size)
                block_obj.channel = data.get("channel", 0)
                if block_obj.channel not in teleporters:
                    teleporters[block_obj.channel] = []
                teleporters[block_obj.channel].append(block_obj)
            elif b_type == "wall":
                block_obj = Wall(data["x"], data["y"], self.block_size)
                
            if block_obj:
                # Zjistíme, jestli se s blokem dá hýbat. Zrcadla, Mixéry atd. jsou defaultně přesouvatelné, ale web to může zakázat.
                default_movable = b_type in ["mirror", "mixer", "colorswitch", "splitter", "crossover"]
                block_obj.movable = data.get("movable", default_movable)
                blocks.append(block_obj)
                
        # Palety barev pro vizuální propojení
        btn_door_colors = [(255, 140, 0), (0, 206, 209), (255, 215, 0), (255, 100, 100)]
        teleport_colors = [(255, 20, 147), (138, 43, 226), (0, 250, 154), (100, 150, 255)]

        # Propojení tlačítek se dveřmi podle jejich ID
        for b in blocks:
            if type(b).__name__ == "Button":
                b.linked_doors = doors.get(b.link_id, [])
                b.link_color = btn_door_colors[b.link_id % len(btn_door_colors)]
            elif type(b).__name__ == "Door":
                b.link_color = btn_door_colors[b.id % len(btn_door_colors)]
                
        # Propojení teleportů navzájem
        for channel, t_list in teleporters.items():
            t_color = teleport_colors[channel % len(teleport_colors)]
            if len(t_list) >= 2:
                t_list[0].linked_teleporter = t_list[1]
                t_list[1].linked_teleporter = t_list[0]
            for t in t_list:
                t.link_color = t_color
                
        return blocks