# 🎮 Flappy Bird: Dark Continent — README

---

## 🧡 Welcome to *Flappy Bird: Dark Continent*

A **spooky, challenging**, and immersive reimagining of the classic Flappy Bird game built with **Python** and **Pygame**.

This version adds dark themes, coins, moving pipes, sound effects, settings, instructions, and high scores. Perfect for those who want a nostalgic yet fresh experience with a twist!
![Screenshot 2025-05-21 100738](https://github.com/user-attachments/assets/887e332b-436d-4a90-a5ee-676fedff5bc0)  ![Screenshot 2025-05-20 212741](https://github.com/user-attachments/assets/bc1bd5d6-6db7-40f8-8f91-98ccabc15d2d)  ![Screenshot 2025-05-21 100802](https://github.com/user-attachments/assets/83497a2a-5c31-40fa-a6ec-5144f491a537)

---

## 🔧 Features

- 🕹️ Playable Game Loop
- 📋 High Score Tracking
- ⚙️ Settings (Volume, Brightness, Controls)
- 📖 Game Instructions Screen
- 🧠 Difficulty Scaling Based on Score
- 💰 Coin Collection System
- 🎵 Spooky Background Music & Sound Effects
- ✨ Centered Top Score Meter While Playing

---

## 📁 Requirements

Make sure you have the following installed:

- Python 3.x
- Pygame (`pip install pygame`)

> Optional: Custom assets like fonts and sounds are used but fallbacks are included.

---

## 📁 Project Structure

```
.
├── flappybirdbg.png         # Background image
├── flappybird.png           # Bird sprite
├── toppipe.png              # Top pipe sprite
├── bottompipe.png           # Bottom pipe sprite
├── flappybirdcoin.png       # Coin sprite
├── flappybirdtitlefont.ttf  # Title font
├── flappybirdmusic.mp3      # Background music
├── flappybirdcrash.mp3      # Crash sound
├── flappybirdcoinmusic.mp3  # Coin pickup sound
├── flappybirdbuttonclicksound.mp3 # Button click sound
└── main.py                  # Main game file
```

> If any of these files are missing, the game will use default assets.

---

## 🧾 How to Play

### Listen Carefully!

1. **Tap spacebar** to fly or face certain doom!
2. **Grab coins**, be a spooky score thief!
3. **Dodge pipes, ground, and sky**—it's ALL evil!
4. Press **ESC** to pause, resume, or flee like a scared specter!

---

## 🎯 Scoring System

- Passing through pipes: +0.5 points
- Collecting coins: +2 points
- Difficulty increases as score rises
- Your score is saved if it makes it to the leaderboard

---

## 🛠️ Controls

| Action     | Key/Button                             |
| ---------- | -------------------------------------- |
| Start Game | Enter after entering name              |
| Jump / Fly | Spacebar or Up Arrow*(configurable)* |
| Pause Game | ESC                                    |
| Click Menu | Mouse click                            |

---

## 🎨 Settings

Customize your gameplay experience:

- 🔊 Volume Control
- 🌑 Brightness Adjustment
- 🖱️ Input Method: `space`, `mouse`, or `up_arrow`

---

## 🏆 High Scores

Your top 10 scores are saved in `highscores.json`.
Beat the high scores and become the ghost king of the skies!

---

## 📦 Installation

1. Clone this repository or download the code
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

---

## 🧩 Development Notes

- All UI elements are centered for readability and immersion
- Font fallback ensures compatibility across systems
- Game state system allows easy expansion/modification
- Clean architecture using classes and modular functions

---

## 📜 Credits

👤 **Developer:** Soleman Hossain
📧 Contact: muzankibu977@gmail.com
📜 Copyright (c) 2025 Soleman Hossain
🔒 All rights reserved.

---

## 🙌 Thank You!

Thank you for playing **Flappy Bird: Dark Continent**!
If you enjoy the game, feel free to fork it, modify it, or challenge friends to beat your high score.

Happy flying... or R.I.P. 😈

---

🎮 **"Good luck... you'll need it!"**
