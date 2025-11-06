# 🎮 QUICK REFERENCE CARD

## 🚀 Quick Start Commands

### Windows (Simulation)
```powershell
.\quick_start.bat
# OR
.venv\Scripts\Activate.ps1
python gesture_control_simulation.py
```

### Raspberry Pi (Hardware)
```bash
./quick_start.sh
# OR
source .venv/bin/activate
python gesture_control_system.py
```

---

## 👋 Gesture Controls

```
┌─────────────────────────────────────────────────────────┐
│                    GESTURE GUIDE                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ☝  NUMBER 1          →  Switch to LED Mode           │
│                                                         │
│  ✌  NUMBER 2          →  Switch to MOTOR Mode         │
│                                                         │
│  ✋  OPEN HAND         →  Turn Device ON               │
│                                                         │
│  ✊  CLOSED FIST       →  Turn Device OFF              │
│                                                         │
│  👍  THUMBS UP (2s)   →  Increase Level (+1)           │
│                                                         │
│  👎  THUMBS DOWN (2s) →  Decrease Level (-1)           │
│                                                         │
│  'Q' KEY              →  Quit Program                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔌 Hardware Connections

```
┌──────────────────────────────────────────────────┐
│         LED CONNECTION (GPIO 18)                 │
├──────────────────────────────────────────────────┤
│                                                  │
│  Pin 12 (GPIO 18) ──→ LED Anode (long leg)     │
│                       ↓                          │
│                    220Ω Resistor                 │
│                       ↓                          │
│                    LED Cathode (short leg)       │
│                       ↓                          │
│                     GND Pin                      │
│                                                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│      SERVO SG90 CONNECTION (GPIO 13)             │
├──────────────────────────────────────────────────┤
│                                                  │
│  Orange/Yellow Wire  →  Pin 33 (GPIO 13)        │
│  Red Wire            →  Pin 2 (5V)              │
│  Brown/Black Wire    →  Pin 6 (GND)             │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 📊 Control Levels

### LED Brightness
```
Level 1: ▁▁▁▁▁  20%  (Dim)
Level 2: ▃▃▃▃▃  40%  (Low)
Level 3: ▅▅▅▅▅  60%  (Medium) ← Default
Level 4: ▇▇▇▇▇  80%  (Bright)
Level 5: ████  100% (Maximum)
```

### Servo Motor Rotation Speed
```
Level 1:  20% ⟲  (Slow)
Level 2:  40% ⟲  (Low-Med)
Level 3:  60% ⟲  (Medium) ← Default
Level 4:  80% ⟲  (Fast)
Level 5: 100% ⟲  (Maximum)
```

**Note**: Motor rotates continuously when ON

---

## 📁 Programs

| Program | Purpose | Platform |
|---------|---------|----------|
| `gesture_control_system.py` | Real hardware control | Raspberry Pi |
| `gesture_control_simulation.py` | Visual simulation | Any computer |
| `gesture_testing.py` | Test gestures | Any computer |

---

## ⚡ Usage Flow

```
1. Test Gestures
   └─→ gesture_testing.py
        └─→ Practice all 6 gestures
             └─→ Check detection accuracy

2. Try Simulation
   └─→ gesture_control_simulation.py
        └─→ See visual LED/motor control
             └─→ Understand mode switching

3. Deploy Hardware (Raspberry Pi)
   └─→ Wire up LED and Servo
        └─→ gesture_control_system.py
             └─→ Control real devices!
```

---

## 🛠️ Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Camera not found | Enable in `raspi-config` |
| Permission denied | Run with `sudo` |
| Gesture not detected | Improve lighting |
| LED not working | Check polarity |
| Servo jittering | Use external 5V power |
| Path error (Windows) | Use `quick_start.bat` |

---

## 💡 Tips

- ✅ Good lighting improves detection
- ✅ Hold hand steady for 2 seconds for thumbs gestures
- ✅ Test in simulation before hardware
- ✅ Use external power for servo to prevent brownout
- ✅ Keep hand within camera frame
- ✅ Press 'q' to quit safely

---

## 📞 Need Help?

1. Read `README_SYSTEM.md` for detailed guide
2. Check `WIRING_GUIDE.md` for connections
3. See `PROJECT_SUMMARY.md` for overview

---

**🎉 Enjoy your gesture-controlled system!**
