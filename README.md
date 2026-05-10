# SpectraMaze

**Logická 2D sci-fi hra v Pythonu (Pygame)**, kde je cílem dostat barevné laserové paprsky ze zdrojových krystalů do cílových žárovek. Hra striktně využívá mechaniku **aditivního míchání barev (RGB)** a je propojená s webovou platformou pro komunitní tvorbu map. Celý projekt se odehrává v pohlcující atmosféře hlubokého vesmíru.

*Vytvořeno jako maturitní/ročníkový projekt se zaměřením na pokročilé využití Objektově orientovaného programování (OOP).*

---

## Hlavní funkce

* **Propojení s webovou platformou:** Uživatelé mohou tvořit vlastní mapy v externím webovém editoru. Mapy jsou ukládány ve formátu JSON přes API do databáze a plynule se načítají do herního klienta.
* **Procedurální AI generátor:** Hra obsahuje komplexní algoritmus pro procedurální generování logických hádanek s garantovanou řešitelností ve třech úrovních obtížnosti.
* **Vlastní audio syntezátor:** Projekt nevyužívá žádné předem nahrané audio samply. Veškeré zvukové efekty jsou v reálném čase matematicky generovány (sine, saw, square, noise) pomocí upraveného pitch-bend enginu.
* **Moderní vizuál a Glassmorphism:** Systém vykreslování zahrnuje animované paralaxní hvězdné nebe s mlhovinou, pulzující neonové prvky a vizuální "skleněné" efekty herního pole.

---

## Architektura a OOP návrh

Projekt je od základů striktně a **kompletně objektově orientovaný**. Každý herní blok je definován vlastní třídou, sdílí společného předka `BaseBlock` a pomocí **polymorfismu** definuje unikátní způsob interakce s běžícím laserovým paprskem.

V rámci specifikace logických překážek (nepřátel) figuruje ve hře **5 stěžejních prvků**, které hráči kříží cestu:
1. **Zrcadlo (Mirror):** Odráží paprsek striktně o 90°.
2. **Mixér (Mixer):** Vynucuje spojení paprsků za vzniku nových barevných kombinací.
3. **Rozdvojník (Splitter):** Tříští energii do více směrů a rozděluje plynulý tok.
4. **Dveře (Door):** Pevná překážka blokující laser, kterou lze otevřít pouze adekvátním aktivačním tlačítkem.
5. **Měnič barev (Color Switch):** Přebarvuje průchozí paprsek, čímž narušuje dříve namíchané spektrum.

### Seznam implementovaných tříd bloků:
* **Krystal (Crystal):** Zdroj světla, vyzařuje primární paprsky (R, G, B).
* **Žárovka (Bulb):** Koncový cíl vyžadující přijetí přesně specifikované barvy energie.
* **Zrcadlo (Mirror):** Mění směr paprsku.
* **Mixér (Mixer):** Provádí aditivní sloučení dvou paprsků.
* **Rozdvojník (Splitter):** Rozštěpí jeden paprsek na dva nezávislé toky.
* **Měnič barev (Color Switch):** Vnutí průchozímu paprsku svou vlastní barvu.
* **Křižovatka (Crossover):** Umožňuje bezpečný překryv tras bez nechtěného smíchání nebo exploze.
* **Dveře a Tlačítko (Door & Button):** Systém logických spínačů pro uvolnění cesty (využití referencí mezi objekty).
* **Teleport (Teleporter):** Přesun paprsku prostorem při zachování jeho parametrů.

---

## Logika míchání barev (RGB)
Hra simuluje fyzikální optické chování aditivního míchání světla. Řešení pokročilých úrovní vyžaduje správné využití skládání spektra:

* 🔴 Červená + 🟢 Zelená = 🟡 **Žlutá**
* 🔴 Červená + 🔵 Modrá = 🟣 **Magenta**
* 🟢 Zelená + 🔵 Modrá = 🩵 **Azurová (Cyan)**
* 🔴 + 🟢 + 🔵 = ⚪ **Bílá**

---

## Instalace a spuštění

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