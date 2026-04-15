# SpectraMaze (Laser puzzle game)

Logická 2D hra v Pythonu (Pygame), kde je cílem dostat barevné laserové paprsky ze zdrojových krystalů do cílových žárovek. Hra striktně využívá mechaniku aditivního míchání barev (RGB) a je propojená s webovou platformou pro komunitní tvorbu map.

**Čtvrtletní projekt - OOP**

## Náplň hry a propojení s webem
Hra se odehrává na čtvercovém herním poli (gridu). Hráč manipuluje s bloky, aby správně nasměroval a obarvil paprsek. 

**Webová platforma:** Zásadní součástí projektu je web, kde uživatelé mohou tvořit vlastní mapy. Tyto mapy si hra stahuje, a funguje zde tabulka hodnocení (Leaderboards), kdo danou mapu vyřešil nejrychleji.

## Splnění požadavků zadání
* **Kompletní OOP:** Všechny bloky z nákresu dědí ze základní třídy `BaseBlock` a využívají polymorfismus při průchodu paprsku.
* **5 druhů nepřátel (Herní překážky):** V naší logické hře funguje jako "nepřítel" 5 hlavních překážkových bloků, které komplikují cestu:
  1. **Zrcadlo** (Odráží paprsek o 90°)
  2. **Míchačka** (Vynucuje spojení barev dle RGB logiky)
  3. **Dveře** (Blokují průchod, dokud není stisknuto tlačítko)
  4. **Switch barev** (Mění barvu procházejícího paprsku)
  5. **Rozdvojník** (Rozděluje paprsek do dvou směrů)
* **Skiny (2 varianty):** GUI a herní pole podporuje změnu vzhledu (např. tmavý/světlý režim), která se dá přepnout v Options menu.
* **Menu:** Obsahuje plně funkční Start menu a Pauza menu (Play, Restart, Options, Quit, výběr jazyka).
* **Levely:** Hra obsahuje komplexní úrovně, které vyžadují logické řetězení bloků.

## Kompletní seznam herních bloků
Ve hře se vyskytují přesně tyto bloky (rozměr 200x200 px):
* **Krystal:** Start paprsku (vysílá R, G nebo B).
* **Žárovka:** Cíl paprsku (vyžaduje specifickou barvu).
* **Zrcadlo:** Odražení paprsku.
* **Míchačka:** Spojení barev.
* **Průchozí blok:** Průchod pro oba paprsky bez smíchání.
* **Dveře:** Otevřou se až po spuštění tlačítka.
* **Tlačítko:** Tlačítko pro otevření dveří.
* **Switch barev:** Blok s možností změnit barvu paprsku.
* **Rozdvojník:** Rozdělení paprsku do dvou.

## Logika spojení barev (RGB)
Hra využívá reálný model míchání světla:
* Červená + Zelená = Žlutá
* Červená + Modrá = Magenta
* Zelená + Modrá = Cyan (Azurová)
* Červená + Zelená + Modrá = Bílá

## Architektura a OOP
Aplikace je zkompilovaná do `.exe` souboru. Kód je rozdělen na:
* `LevelManager` (stahování map z webu a správa gridu)
* `LaserEngine` (výpočet RGB logiky a tras paprsků)
* `GUI_Manager` (správa Start/Pauza menu a herního pole)
