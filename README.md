# Zombie Whack Game

A fun whack-a-mole style game where you whack zombies that appear from graves!

## Project Structure

```
LTG/
├── README.md
├── .gitignore
└── BTL1_LTG/          # Main game folder
    ├── zombie_whack.py    # Main game file
    ├── test_grave.py      # Test file
    ├── .venv/             # Python virtual environment
    └── assets/            # Game assets
        ├── zombieN.png
        ├── graveN.png
        ├── background.jpg
        ├── heart_full.png
        ├── heart_empty.png
        ├── hit.mp3
        └── bgmusic.mp3
```

## Features

- **Timer Mode**: Toggle zombie auto-disappear timer on/off
- **Lives System**: Heart-based life counter with visual hearts
- **Pause Menu**: Press ESC during gameplay to pause
- **Customizable Round Time**: Adjust game duration (30s to 5 minutes)
- **Statistics Tracking**: Hits, misses, escaped zombies, and accuracy
- **Asset Support**: Custom graphics and sounds

## Controls

- **Left Click**: Whack zombies
- **ESC**: Pause/Resume game (during gameplay)
- **R**: Reset scores only
- **T**: Toggle timer mode during gameplay

## Assets

Place these optional asset files in the same directory as the game:

- `zombieN.png` - Zombie head image
- `graveN.png` - Grave/hole image  
- `background.jpg` - Background image
- `heart_full.png` - Full heart icon
- `heart_empty.png` - Empty heart icon
- `hit.mp3` - Hit sound effect
- `bgmusic.mp3` - Background music

## Requirements

- Python 3.x
- Pygame 2.x

## Installation

1. Clone this repository: `git clone https://github.com/KeHamTruyen/LTG.git`
2. Navigate to the game folder: `cd LTG/BTL1_LTG`
3. Install pygame: `pip install pygame`
4. Run the game: `python zombie_whack.py`

## How to Play

1. Start the game from the main menu
2. Configure timer mode and round duration
3. Click on zombies as they appear from graves
4. Avoid missing clicks (costs lives)
5. Game ends when lives reach 0 or time runs out (in timer mode)

## Game Modes

- **Timer ON**: Zombies auto-disappear, game has time limit
- **Timer OFF**: Zombies stay until clicked, game continues until lives are lost

Have fun whacking zombies! 🧟‍♂️
