# GEX text editor
GEX is a simple line-based text editor inspired by ex. It allows users to manipulate text files through a command-line interface.

## Usage
run gex with an empty buffer
```
./gex.py
```

| Commands | Parameters | Usage |
| --- | --- | --- |
| `a` | (optional) `line` `text` | append text at `line` if provided, otherwise at the cursor. appended text can be `text` or if not provided, prompt for text line by line until given `.` |
| `i` | (optional) `line` `text` | insert text at `line` if provided, otherwise at the cursor. inserted text can be `text` or if not provided, prompt for text line by line until given `.` |
| `d` | (optional) `line` | delete line at `line` if provided, otherwise at the cursor |
| (none) | `line` | move cursor to `line` |
| `s` | (none) | show editor state including buffer name, current line and total lines |
| `v` | (optional) `line range` | print lines in `line range` if provided, otherwise print the enter file |
| `r` | (none) | read file into buffer, prompt for file name |
| `w` | (none) | write buffer, prompt for name if buffer is not named |
| `q` | (none) | quit editor |