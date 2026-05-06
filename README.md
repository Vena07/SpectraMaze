# 🌌 SpectraMaze

**Logická 2D sci-fi hra v Pythonu (Pygame)**, kde je cílem dostat barevné laserové paprsky ze zdrojových krystalů do cílových žárovek. Hra striktně využívá mechaniku **aditivního míchání barev (RGB)** a je propojená s webovou platformou pro komunitní tvorbu map. Hra se odehrává v pohlcující atmosféře hlubokého vesmíru.

🏆 *Vytvořeno jako čtvrtletní maturitní/školní projekt zaměřený na Objektově orientované programování (OOP).*

---

## ✨ Hlavní funkce

* 🌐 **Propojení s Webovou Platformou:** Uživatelé tvoří vlastní mapy v externím webovém editoru. Mapy jsou ukládány jako kompaktní JSON přes API přímo do online databáze a stahují se plynule rovnou do hry.
* 🤖 **Procedurální AI Generátor:** Neomezený počet logických hádanek! Hra obsahuje algoritmus, který umí generovat smysluplné, zaručeně řešitelné mapy ve 3 úrovních obtížnosti.
* 🎵 **Vlastní Audio Syntezátor:** Žádné předem nahrané audio samply pro herní bloky. Hra si v reálném čase matematicky generuje sci-fi zvukové vlny (sine, saw, square, noise) pomocí upraveného pitch-bend enginu.
* 🪐 **Moderní Vizuál & Glassmorphism:** Animované paralaxní hvězdné nebe s mlhovinou, pulzující neonové prvky a vizuální "skleněné" efekty herního pole.

---

## 🧩 Architektura a OOP zadání

Projekt je od základů striktně a **kompletně objektově orientovaný**. Každý herní blok je definován vlastní třídou, sdílí společného předka `BaseBlock` a pomocí **polymorfismu** definuje unikátní způsob interakce s běžícím laserovým paprskem.

V rámci specifikace "Nepřátelé" figuruje ve hře **5 stěžejních logických překážek**, které hráči kříží cestu:
1. **Zrcadlo (Mirror):** Odráží paprsek striktně o 90°.
2. **Mixér (Mixer):** Neúprosně vynucuje spojení paprsků do nových barev.
3. **Rozdvojník (Splitter):** Tříští energii do více směrů a narušuje plynulý tok.
4. **Dveře (Door):** Ocelová překážka, kterou nelze zdolat bez nalezení aktivačního tlačítka.
5. **Měnič (Color Switch):** Zákeřně přebarvuje už správně namíchaný paprsek.

### Kompletní arzenál (Bloky):
* 💎 **Krystal:** Zdroj světla, střílí primární paprsky (R, G, B).
* 💡 **Žárovka:** Koncový cíl, který vyžaduje přesně specifikovanou barvu energie.
* 🪞 **Zrcadlo:** Odráží paprsky.
* 🎛️ **Mixér:** Kombinuje 2 paprsky do jedné barvy.
* 🔀 **Rozdvojník:** Rozštěpí 1 paprsek na 2 nezávislé.
* 🔄 **Měnič barev:** Přebarví průchozí paprsek na svou barvu.
* ❌ **Křižovatka:** Bezpečný překryv tras bez exploze.
* 🚪 **Dveře** & 🔘 **Tlačítko:** Logické spínače pro uvolnění cesty.
* 🌀 **Teleport:** Cestování prostorem ve zlomku sekundy.

---

## 🎨 Logika míchání barev (RGB)
Hra simuluje skutečné optické chování aditivního míchání světla. Abyste dokázali vyřešit ty nejtěžší úrovně, budete muset využít skládání spektra:

* 🔴 Červená + 🟢 Zelená = 🟡 **Žlutá**
* 🔴 Červená + 🔵 Modrá = 🟣 **Magenta**
* 🟢 Zelená + 🔵 Modrá = 🩵 **Azurová (Cyan)**
* 🔴 + 🟢 + 🔵 = ⚪ **Bílá**

---

## ⚙️ Instalace a Spuštění

1. **Naklonujte si repozitář**
```bash
git clone https://github.com/vasin/SpectraMaze.git
cd SpectraMaze
```

2. **Nainstalujte závislosti** (K běhu je zapotřebí knihovna `pygame` a `requests`)
```bash
pip install pygame requests
```

3. **Spusťte hru**
```bash
python main.py
```

---

## 📁 Struktura složek projektu

```text
SpectraMaze/
│
├── main.py                # Jádro, herní smyčka, synth engine a částicové efekty
├── engine.py              # Logika výpočtu letu laseru a detekce kolizí
├── ui.py                  # Pokročilý UI systém, Glassmorphism menu, animace náhledů
├── level_manager.py       # Komunikace s webovým API, stahování JSON a procedurální generátor
│
├── blocks/                # Třídy všech herních bloků
│   ├── __init__.py
│   ├── base_block.py      # OOP: Společný předek
│   ├── crystal.py
│   ├── bulb.py
│   ├── mirror.py
│   ├── mixer.py
│   ├── crossover.py
│   ├── door.py
│   ├── button.py
│   ├── color_switch.py
│   ├── teleporter.py
│   └── splitter.py
│
└── sound/                 # Podkladový soundtrack (pokud je k dispozici)