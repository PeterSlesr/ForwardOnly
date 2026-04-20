# ForwardOnly

A minimal Windows writing tool that lets you move forward only.

---

## What it does

ForwardOnly opens a writing session where:
- Only the last N words are visible (default: 5, configurable)
- Backspace, delete, and arrow keys are blocked
- Text is saved to a plain `.txt` file when you close the session
- You can open the same file in Notepad anytime to review or edit freely

---

## Download

Go to the [Releases](../../releases) page and download `ForwardOnly.exe`.  
No installation needed. Double-click to run.

---

## How to use

### Setting up a project

A "project" is just a folder with one `.txt` file in it.

1. Create a folder anywhere on your computer (e.g. `my-novel`)
2. Either put an existing `.txt` file in it, or let ForwardOnly create one for you

### Writing

1. Open `ForwardOnly.exe`
2. Click **Open Project Folder** and select your project folder
3. Set your word window size (default: 5)
4. Click **Write**
5. A new window opens showing the last N words of your existing text
6. Type forward — only forward
7. Close the window (or press `Escape`) to save and return to the launcher

### Reviewing

1. Open your project as above
2. Click **Review**
3. Your `.txt` file opens in Notepad (or your default text editor)
4. Edit freely, save normally

---

## Project structure

```
my-novel/
  my-novel.txt              ← your writing
  .focus_settings.json      ← window size preference (auto-created, safe to ignore)
```

---

## Building from source

Requirements: Python 3.11+

```bash
pip install pyinstaller
pyinstaller ForwardOnly.spec
# output: dist/ForwardOnly.exe
```

---

## Releasing a new version (GitHub)

1. Commit your changes
2. Tag the commit:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions will automatically build `ForwardOnly.exe` and attach it to the release

---

## License

MIT
