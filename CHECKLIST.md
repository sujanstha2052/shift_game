# 📋 Game Off 2026: Shift/Return — Development Checklist

> **Theme**: SHIFT!  
> **Target Jam Submission**: November 28, 2026 (Buffer ahead of final deadline)

---

## 📅 Week 1: Core Architecture, Polish & QoL (Nov 2 – Nov 8)

*Goal: Make the current prototype feel smooth, responsive, and robust with foundational puzzle game quality-of-life features.*

### Architecture & Game State Machine
- [x] Refactor game loop out of `main.py` into a structured state manager in `src/game.py`
- [x] Implement scene management interface (`TitleScene`, `GameScene`, `LevelClearScene`, `PauseScene`)
- [x] Create a centralized input handler to support both keyboard and future gamepad controls

### Movement & Polish
- [x] Implement smooth tile interpolation (lerping / tweening) instead of instant coordinate snapping
- [x] Add directional facing or squish/stretch animations when moving
- [x] Add wall-bump feedback (subtle bounce / sound trigger on invalid move)

### Essential Puzzle Quality-of-Life (Crucial for Jam Reviewers)
- [x] Implement **Undo System (`Z` / `U`)** with a state history stack:
  - [x] Restore player position
  - [x] Restore dimension state (Normal vs. Corrupted)
  - [x] Restore rebooted terminal states
  - [x] Restore block positions (for upcoming mechanics)
- [x] Implement **Instant Restart (`R`)** with zero loading time
- [x] Implement **Level Select / Skip Menu** for debugging and playtesting

### Shifting Juice & Feedback
- [x] Add visual & audio rejection feedback when phasing into a solid wall (screen shake, error buzz, red flash)
- [x] Add transition effect when shifting realities (horizontal scanline wipe / chromatic aberration flash)
- [x] Add subtle idle pulse / glow animation for terminals

---

## 📅 Week 2: Mechanics Expansion & Audio System (Nov 9 – Nov 15)

*Goal: Introduce new puzzle elements that interact across both dimensions, and build the soundscape.*

### New Dimension-Interacting Mechanics
- [x] **RAM Blocks (Pushable Memory Crates)**:
  - [x] Pushable by player if space behind is clear
  - [x] Can exist in Normal, Corrupted, or Both dimensions
  - [x] Usable to weigh down pressure plates or block laser paths
- [x] **Firewalls / Conduits (Laser Barriers)**:
  - [x] Laser beams active in one dimension and harmless conduits in the other
  - [x] Blocks player movement when active
- [x] **Corrupted Daemons / Sentinels**:
  - [x] Security subroutines that patrol fixed paths
  - [x] Only move / alert when the player is inside the Corrupted Dimension
- [x] **Data Pressure Plates**:
  - [x] Toggle firewalls or open access gates when pressed by player or RAM blocks

### Audio System & Sound Design
- [x] Initialize `pygame.mixer` with dedicated channels (Music, SFX, UI)
- [x] Create / source chiptune & retro sound effects:
  - [x] Player step click
  - [x] Dimension shift sub-bass whoosh / phase sound
  - [x] Terminal reboot success chime
  - [x] Error / invalid shift buzz
  - [x] Sector cleared fanfare
- [x] Add background ambient synth tracks:
  - [x] Normal Dimension theme (calm, rhythmic electronic hum)
  - [x] Corrupted Dimension filter (muffled low-pass or glitched version of the track)

---

## 📅 Week 3: Level Design, Narrative & Visual Juicing (Nov 16 – Nov 22)

*Goal: Craft a satisfying puzzle progression curve, integrate the night shift narrative, and polish visuals.*

### Sector & Level Design (10–12 Total Levels)
- [ ] **Sector 1: Sub-Routine (Levels 1–4)**:
  - [ ] Level 01: "Severed Connection" (Intro to movement & Shift mechanics)
  - [ ] Level 02: "Memory Leak" (Alternating wall barriers)
  - [ ] Level 03: "Cache Miss" (Multi-room routing & cross-dimension terminals)
  - [ ] Level 04: "Stack Overflow" (Tight corridors requiring precision shifts)
- [ ] **Sector 2: Memory Heap (Levels 5–8)**:
  - [ ] Level 05: "Pointer Arithmetic" (Introduction to pushable RAM blocks)
  - [ ] Level 06: "Firewall Protocol" (Laser gates and toggle switches)
  - [ ] Level 07: "Defrag Sequence" (Cross-dimensional block placement)
  - [ ] Level 08: "Buffer Overflow" (Combining blocks, lasers, and terminals)
- [ ] **Sector 3: Kernel Core (Levels 9–12)**:
  - [ ] Level 09: "Daemon Patrol" (Introducing stealth around corrupted sentinels)
  - [ ] Level 10: "Race Condition" (Timing shifts around moving hazards)
  - [ ] Level 11: "Deadlock" (Complex multi-stage spatial reasoning)
  - [ ] Level 12: "Root Access" (Final master puzzle combining all mechanics)

### Narrative & Theme Integration
- [ ] Add opening intro briefing ("OmniCorp Graveyard Shift Notice: Mainframe Breach")
- [ ] Add humorous sysadmin email / ticket logs displayed upon rebooting servers:
  - [ ] *"Ticket #102: Printer in accounting is summoning demons again."*
  - [ ] *"Ticket #404: Who pushed directly to production on Friday evening?"*
- [ ] Add ending sequence ("Shift Complete: Clocking Out").

### Visual Juicing & CRT Shader
- [ ] Particle burst when rebooting a terminal
- [ ] Floating dust / digital glitch bits in corrupted dimension
- [ ] CRT scanline overlay or subtle screen vignette toggle in settings

---

## 📅 Week 4: Playtesting, Packaging & Submission (Nov 23 – Nov 28)

*Goal: Ensure seamless distribution, test difficulty, and complete the itch.io game jam submission.*

### Playtesting & Balancing
- [ ] Blind playtest with external testers (check for softlocks, confusing puzzles, difficulty spikes)
- [ ] Verify every level is solvable with an optimal move counter
- [ ] Add step counter and par scores per level for replayability

### Distribution & Web Port (`pygbag`)
- [ ] Configure `pygbag` for WebAssembly execution in modern web browsers
- [ ] Test web build performance, audio autoplay policies, and fullscreen toggle
- [ ] Generate desktop binaries using PyInstaller:
  - [ ] Windows (`.exe` standalone / zip)
  - [ ] macOS (`.app` / standalone bundle)
  - [ ] Linux executable

### Itch.io Storefront & Jam Media
- [ ] Create animated gameplay GIFs demonstrating:
  - [ ] The core dimension shift effect
  - [ ] Pushing RAM blocks across dimensions
  - [ ] Terminal rebooting sequence
- [ ] Design cover banner ($630 \times 500\text{px}$) and screenshot gallery
- [ ] Write punchy game description with controls list and Game Off credits
- [ ] Upload builds, configure web player embed, and submit to **GitHub Game Off 2026** by **Nov 28**
