Here's how to run your Wumpus World project based on the folder structure and files we've created:

### **1. First-Time Setup**
```bash
# Navigate to project root
cd wumpus

# Install dependencies
pip install -r requirements.txt  # Ensures pygame and other packages are installed

# Generate sample worlds (optional)
python -m src.environment.world_generator
```

---

### **2. Running the Game**
You have **three main ways** to run the project:

#### **Option 1: Graphical Mode (AI Agent)**
```bash
# Default (auto mode with GUI)
python -m src.game.wumpus

# With custom world
python -m src.game.wumpus --world worlds/hard.world

# Options:
# --mode [auto|manual]  # Auto=AI plays, Manual=keyboard control
# --no-gui              # Disable graphics
# --difficulty [easy|medium|hard]
```

#### **Option 2: Text-Based CLI**
```bash
# Pure command-line interface
python -m src.interface.cli --world worlds/easy.world
```

#### **Option 3: Manual Control (GUI)**
```bash
python -m src.game.wumpus --mode manual
```
*Use these commands in-game:*
- `move up/down/left/right`
- `shoot up/down/left/right`
- `grab`
- `status`
- `quit`

---

### **3. Key Files and Their Roles**
| File | Purpose | How to Customize |
|------|---------|------------------|
| `worlds/*.world` | Pre-built maps | Edit with any text editor |
| `src/agent/logic.py` | AI decision logic | Modify resolution algorithms |
| `src/interface/graphical_control.py` | GUI appearance | Change colors/animations |
| `src/environment/world_generator.py` | Random world rules | Adjust `min_pits`, `wumpus_count` etc. |

---

### **4. Debugging & Testing**
```bash
# Run all tests
python -m pytest tests/

# Test specific component (e.g., agent)
python -m pytest tests/test_agent.py

# Debug world generation
python -c "from src.environment.world_generator import WorldGenerator; WorldGenerator().generate_sample_worlds()"
```

---

### **5. Example Scenarios**
#### **Run AI on Hard Difficulty**
```bash
python -m src.game.wumpus --difficulty hard --mode auto
```
*Output (GUI):*  
- Visualizes agent's knowledge (green=safe, red=risky)  
- Animates arrow shots and Wumpus deaths  

#### **Create Custom World**
1. Edit `worlds/custom.world`:
   ```
   -----G----
   ----P-----
   ----------
   --W-------
   ----------
   A---------
   ```
2. Run:
   ```bash
   python -m src.game.wumpus --world worlds/custom.world
   ```

---

For fastest start:
```bash
python -m src.game.wumpus  # GUI + AI
python -m src.interface.cli  # Pure text mode
```