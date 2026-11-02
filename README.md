# Shift/Return ⚡️

A 2D dimension-shifting puzzle game built with Python and [pygame-ce](https://pyga.me/) for **GitHub Game Off 2026**.

In **Shift/Return**, you play as a system administrator navigating a corrupted mainframe. To stabilize the facility, you must traverse between two parallel layers—the **Normal Dimension** (Server Room) and the **Corrupted Dimension** (System Glitch)—to reboot offline servers and reach the sector exit.

---

## 🎮 Gameplay & Mechanics

- **Dual-Dimension Shifting (`Shift`)**: Toggle between the Normal and Corrupted states of the sector. Walls and pathways shift based on your active reality.
- **Phase Constraints**: You can only shift if your current coordinates are empty floor space in the destination dimension—materializing inside a wall is strictly prohibited!
- **Server Rebooting**: Offline terminals (amber) exist across both dimensions. Step on each terminal in its corresponding reality to reboot it (neon green).
- **Sector Exits**: The exit gateway stays locked (red) until all terminals in the sector are rebooted. Once unlocked (green), step through to clear the level.

---

## 🕹️ Controls

| Action | Keybinding |
| :--- | :--- |
| **Move** | `W`, `A`, `S`, `D` or `Arrow Keys` |
| **Dimension Shift** | `Left Shift` or `Right Shift` |
| **Proceed / Restart** | `Enter` (when sector is cleared) |
| **Exit Game** | `Esc` |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- A virtual environment tool (`venv`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd shift_game
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On macOS/Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows:
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

Launch the game with:
```bash
python main.py
```

---

## 📁 Project Structure

```text
shift_game/
├── assets/                 # Game assets
│   ├── audio/              # Sound effects and background music
│   ├── fonts/              # Custom typography and font files
│   └── images/             # Sprites and texture tiles
├── src/                    # Source code modules
│   ├── config.py           # Resolution, grid constants, and color palettes
│   ├── game.py             # Game state management
│   ├── interactables.py    # Terminal and ExitDoor object logic
│   ├── level.py            # Level state, shift checks, and map renderer
│   ├── levels_data.py      # Tilemaps and entity coordinate definitions
│   └── player.py           # Player movement and drawing
├── main.py                 # Application entry point and game loop
├── requirements.txt        # Project dependencies (pygame-ce)
└── README.md               # Documentation
```

---

## 🛠️ Built With

- **[Python](https://www.python.org/)**
- **[pygame-ce](https://github.com/pygame-community/pygame-ce)** — Community-driven fork of Pygame
