# Question Editor

A simple GUI application for editing JSON question files.

## Requirements

- Python 3.x
- tkinter (stdlib for Python)
- Pillow (`pip install Pillow`)

## Installation

```bash
pip install Pillow
```

## Usage

1. Run the script inside an `output/{year}` folder containing a `questions/` subdirectory with question folders:

```bash
python question_editor.py
```

## Features

- Edit question metadata (title, index, year, language, discipline)
- Edit question context and alternatives introduction
- Edit alternatives (A-E) with correct answer selection
- Parse alternatives from text
- Manage question images (add, remove, replace, reorder)
- Preview images in the editor
- Double-click images to insert them into the context
- Jump to any question by number
- Save changes with `Ctrl+S`

## Navigation

- Use **Previous** and **Next** buttons to navigate between questions
- Or type a question number in the jump input and press **Tab** to jump directly