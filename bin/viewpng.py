#!/usr/bin/env python3
"""Pan/zoom a PNG in a kitty-graphics terminal. Keys: +/- zoom, arrows/hjkl pan, 0 fit, 1 100%, [ ] prev/next, q quit."""
import sys, os, base64, struct, termios, tty, fcntl, select

args = sys.argv[1:]
idx = 0
if args and args[0].startswith("--start="):
    idx = int(args.pop(0)[8:])
paths = args
idx = min(max(idx, 0), len(paths) - 1)
out = sys.stdout

def png_size(p):
    with open(p, 'rb') as f:
        h = f.read(24)
    return struct.unpack('>II', h[16:24])

def term():
    ws = struct.unpack('HHHH', fcntl.ioctl(1, termios.TIOCGWINSZ, b'\0' * 8))
    rows, cols, xpx, ypx = ws
    cw = xpx / cols if xpx else 10
    ch = ypx / rows if ypx else 20
    return rows, cols, cw, ch

def send(p, x, y, w, h, c, r):
    data = base64.standard_b64encode(open(p, 'rb').read()).decode()
    chunks = [data[i:i + 4096] for i in range(0, len(data), 4096)]
    for i, d in enumerate(chunks):
        m = 1 if i < len(chunks) - 1 else 0
        ctrl = f"a=T,f=100,i=1,q=2,x={x},y={y},w={w},h={h},c={c},r={r},C=1,m={m}" if i == 0 else f"m={m}"
        out.write(f"\x1b_G{ctrl};{d}\x1b\\")

state = {}
def reset(p):
    W, H = png_size(p)
    state.update(W=W, H=H, zoom=1.0, cx=W / 2, cy=H / 2)

def draw():
    p = paths[idx]
    W, H = state['W'], state['H']
    rows, cols, cw, ch = term()
    r_avail, c_avail = rows - 2, cols
    box_w, box_h = c_avail * cw, r_avail * ch
    fit = min(box_w / W, box_h / H)          # screen px per image px at "fit"
    scale = fit * state['zoom']
    vw = min(W, box_w / scale)               # visible source size
    vh = min(H, box_h / scale)
    state['cx'] = min(max(state['cx'], vw / 2), W - vw / 2)
    state['cy'] = min(max(state['cy'], vh / 2), H - vh / 2)
    x, y = int(state['cx'] - vw / 2), int(state['cy'] - vh / 2)
    w, h = max(1, int(vw)), max(1, int(vh))
    c = max(1, min(c_avail, round(w * scale / cw)))
    r = max(1, min(r_avail, round(h * scale / ch)))
    out.write("\x1b[2J\x1b[H\x1b_Ga=d,d=A\x1b\\")
    send(p, x, y, w, h, c, r)
    out.write(f"\x1b[{rows};1H\x1b[2K{idx + 1}/{len(paths)} {os.path.basename(p)}  {W}x{H}  zoom {state['zoom']:.2f}x  +/- zoom  arrows pan  0 fit  [ ] prev/next  q quit")
    out.flush()
    return vw, vh

def key():
    b = os.read(0, 8).decode(errors='ignore')
    return b

fd = 0
old = termios.tcgetattr(fd)
try:
    tty.setcbreak(fd)
    out.write("\x1b[?25l")
    reset(paths[idx])
    vw, vh = draw()
    while True:
        k = key()
        step = 0.15
        if k in ('q', '\x03'): break
        elif k in ('+', '='): state['zoom'] = min(state['zoom'] * 1.25, 40)
        elif k in ('-', '_'): state['zoom'] = max(state['zoom'] / 1.25, 1.0)
        elif k == '0': state['zoom'] = 1.0; state['cx'], state['cy'] = state['W'] / 2, state['H'] / 2
        elif k in ('\x1b[D', 'h'): state['cx'] -= vw * step
        elif k in ('\x1b[C', 'l'): state['cx'] += vw * step
        elif k in ('\x1b[A', 'k'): state['cy'] -= vh * step
        elif k in ('\x1b[B', 'j'): state['cy'] += vh * step
        elif k == ']' and idx < len(paths) - 1: idx += 1; reset(paths[idx])
        elif k == '[' and idx > 0: idx -= 1; reset(paths[idx])
        else: continue
        vw, vh = draw()
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old)
    out.write("\x1b_Ga=d,d=A\x1b\\\x1b[?25h\x1b[2J\x1b[H")
    out.flush()
