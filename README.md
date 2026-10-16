# claude-shots

A [Claude Code](https://claude.com/claude-code) mod for looking at the screenshots your agent takes without leaving the terminal.

It watches tool calls for absolute `.png` paths (for example a verification run that saves screenshots) and adds a `/shot` command that opens them in a **zoomable, pannable viewer in a new [herdr](https://herdr.dev) split**.

## Install

```
/plugin install shots --marketplace paulund/claude-shots
```

## Use

| Command | What it does |
| --- | --- |
| `/shot` | Open the latest screenshot (all session screenshots are loaded) |
| `/shot N` | Start on the Nth screenshot |
| `/shot list` | Print every screenshot path seen this session |

Viewer keys (click the new pane first): `+` / `-` zoom, arrows or `h j k l` pan, `0` fit, `[` / `]` previous / next, `q` quit.

## Requirements

- A terminal with the kitty graphics protocol (Ghostty, kitty, WezTerm).
- [herdr](https://herdr.dev), which passes graphics through and provides the split. Outside herdr, `/shot` prints the command to run `bin/viewpng.py` yourself.
- `python3`.

The viewer (`bin/viewpng.py`) is standalone: `python3 bin/viewpng.py a.png b.png`.

## How zoom works

It crops the source image and lets the terminal scale the crop (kitty graphics `x,y,w,h` source rectangle), so zoomed text stays sharp.
