#!/usr/bin/env python3
"""
Silakka54 Terminal Trainer
A curses-based typing practice game for your Silakka54 split keyboard.
Usage: python3 silakka54_trainer.py
"""

import curses
import time
import random
import sys

# ── WORD BANKS ───────────────────────────────────────────────────────────────

WORDS = {
    0: [
        "the quick brown fox jumps over the lazy dog",
        "split keyboard feels strange at first but gets better",
        "column stagger helps reduce finger travel distance",
        "practice makes perfect with any new keyboard layout",
        "left hand types the left side right hand types right",
        "arch linux is a great operating system for developers",
        "writing code on a split keyboard feels ergonomic",
        "your fingers will thank you after a long typing session",
        "the home row is where your fingers should rest comfortably",
        "take breaks and stretch your wrists while learning",
        "muscle memory takes time to build so be patient",
        "try to keep your eyes on the screen not the keys",
    ],
    1: [
        "hold mo1 then press h j k l for arrow keys",
        "navigate without leaving the home row position",
        "use home and end to jump to the edges of a line",
        "page up and page down scroll through long files",
        "vim uses hjkl arrows and your layer matches perfectly",
        "hold right thumb and move cursor anywhere you need",
        "left arrow right arrow up arrow down arrow",
        "jump to home jump to end navigate the document",
    ],
    2: [
        "function hello() { return 'world'; }",
        "const arr = [1, 2, 3];",
        "if (x > 0 && y < 100) { return true; }",
        "import { useState } from 'react';",
        "let result = (a + b) * (c - d);",
        "const obj = { key: 'value', num: 42 };",
        "for (let i = 0; i < arr.length; i++) {}",
        "export default function App() { return null; }",
        "git commit -m 'fix: update keyboard config'",
        "const [state, setState] = useState(null);",
        "sudo pacman -S python python-pip curl wget",
        "grep -r 'TODO' src/ | wc -l",
    ],
    3: [
        "function split() { return keyboard.split(''); }",
        "the quick brown fox { jumps: 'over' } the lazy dog",
        "import React from 'react'; // best library",
        "let wpm = (chars / 5) / (time / 60);",
        "arch linux + silakka54 = productivity boost",
        "const layers = [0, 1, 2, 3]; // four layers total",
        "if (streak > 10) { console.log('nice work!'); }",
        "export const config = { split: true, layers: 4 };",
        "while (learning) { practice(); improve(); }",
        "python3 -c \"print('hello from the terminal')\"",
    ],
}

MODE_NAMES = {
    0: "Base L0 ",
    1: "Nav L1  ",
    2: "Sym L2  ",
    3: "Mixed   ",
    4: "KeyFlash",
}

MODE_DESCS = {
    0: "Base QWERTY — get comfy with the split & column stagger",
    1: "Nav layer — MO1 + hjkl=arrows, y/n=pgup/dn, u/o=home/end",
    2: "Symbols — MO2 + brackets ( ) [ ] { } operators = + - _",
    3: "Mixed — everything at once, base + symbols + nav hints",
    4: "Key Flash — type the displayed key from any layer  [h]=hint  [f]=filter",
}

MODE_COLORS = {0: 7, 1: 4, 2: 3, 3: 5, 4: 1}  # white, cyan, yellow, magenta, green

# ── LAYER HINTS ──────────────────────────────────────────────────────────────

LAYER2_KEYS = {
    '(': 'MO2+Y', ')': 'MO2+U', '+': 'MO2+I', '=': 'MO2+O', "'": 'MO2+P',
    '{': 'MO2+H', '}': 'MO2+J', '-': 'MO2+K', '_': 'MO2+L',
    '[': 'MO2+N', ']': 'MO2+M',
    '`': 'MO2+T', '~': 'MO2+G', '|': 'MO2+V', '\\': 'MO2+B',
    '"': 'MO2+P',
}


def get_hint(char):
    if char in LAYER2_KEYS:
        return f"[SYM] {LAYER2_KEYS[char]}"
    return ""


# ── KEY FLASH CHALLENGE POOL ─────────────────────────────────────────────────
# curses.KEY_* are module-level integer constants, safe to use here.
# L3 hints are based on the v4 keymap; verify against your keymap PDF if unsure.

KEY_CHALLENGES = [
    # ── L1 Navigation (MO1 = right thumb middle) ──────────────────────────
    {'display': '←',    'name': 'Left Arrow',  'keys': [curses.KEY_LEFT],   'layer': 1, 'hint': 'MO1 + H'},
    {'display': '↓',    'name': 'Down Arrow',  'keys': [curses.KEY_DOWN],   'layer': 1, 'hint': 'MO1 + J'},
    {'display': '↑',    'name': 'Up Arrow',    'keys': [curses.KEY_UP],     'layer': 1, 'hint': 'MO1 + K'},
    {'display': '→',    'name': 'Right Arrow', 'keys': [curses.KEY_RIGHT],  'layer': 1, 'hint': 'MO1 + L'},
    {'display': 'PgUp', 'name': 'Page Up',     'keys': [curses.KEY_PPAGE],  'layer': 1, 'hint': 'MO1 + Y'},
    {'display': 'PgDn', 'name': 'Page Down',   'keys': [curses.KEY_NPAGE],  'layer': 1, 'hint': 'MO1 + N'},
    {'display': 'Home', 'name': 'Home',        'keys': [curses.KEY_HOME],   'layer': 1, 'hint': 'MO1 + U'},
    {'display': 'End',  'name': 'End',         'keys': [curses.KEY_END],    'layer': 1, 'hint': 'MO1 + O'},
    # ── L2 Symbols (MO2 = left thumb middle) ──────────────────────────────
    {'display': '(',  'name': 'Open Paren',    'keys': [ord('(')],  'layer': 2, 'hint': 'MO2 + Y'},
    {'display': ')',  'name': 'Close Paren',   'keys': [ord(')')],  'layer': 2, 'hint': 'MO2 + U'},
    {'display': '+',  'name': 'Plus',          'keys': [ord('+')],  'layer': 2, 'hint': 'MO2 + I'},
    {'display': '=',  'name': 'Equals',        'keys': [ord('=')],  'layer': 2, 'hint': 'MO2 + O'},
    {'display': "'",  'name': 'Single Quote',  'keys': [ord("'")],  'layer': 2, 'hint': 'MO2 + P'},
    {'display': '{',  'name': 'Open Brace',    'keys': [ord('{')],  'layer': 2, 'hint': 'MO2 + H'},
    {'display': '}',  'name': 'Close Brace',   'keys': [ord('}')],  'layer': 2, 'hint': 'MO2 + J'},
    {'display': '-',  'name': 'Minus',         'keys': [ord('-')],  'layer': 2, 'hint': 'MO2 + K'},
    {'display': '_',  'name': 'Underscore',    'keys': [ord('_')],  'layer': 2, 'hint': 'MO2 + L'},
    {'display': '[',  'name': 'Open Bracket',  'keys': [ord('[')],  'layer': 2, 'hint': 'MO2 + N'},
    {'display': ']',  'name': 'Close Bracket', 'keys': [ord(']')],  'layer': 2, 'hint': 'MO2 + M'},
    {'display': '`',  'name': 'Backtick',      'keys': [ord('`')],  'layer': 2, 'hint': 'MO2 + T'},
    {'display': '~',  'name': 'Tilde',         'keys': [ord('~')],  'layer': 2, 'hint': 'MO2 + G'},
    {'display': '|',  'name': 'Pipe',          'keys': [ord('|')],  'layer': 2, 'hint': 'MO2 + V'},
    {'display': '\\', 'name': 'Backslash',     'keys': [ord('\\')], 'layer': 2, 'hint': 'MO2 + B'},
    # ── L3 Function Keys (MO3 = left thumb inner) ─────────────────────────
    # Left hand home row: A=M0, S=F1, D=F2, F=F3, G=F4
    # Right hand home row: H=Vol-, J=Prev, K=F9, L=F10, ;=F11, '=F12
    # Right hand top row:  Y=Vol+, U=Next, I=Play, O=PrtSc
    # Right hand bot row:  N=F5, M=F6, ,=F7, .=F8, /=Gui
    {'display': 'F1',  'name': 'F1',  'keys': [curses.KEY_F1],  'layer': 3, 'hint': 'MO3 + S'},
    {'display': 'F2',  'name': 'F2',  'keys': [curses.KEY_F2],  'layer': 3, 'hint': 'MO3 + D'},
    {'display': 'F3',  'name': 'F3',  'keys': [curses.KEY_F3],  'layer': 3, 'hint': 'MO3 + F'},
    {'display': 'F4',  'name': 'F4',  'keys': [curses.KEY_F4],  'layer': 3, 'hint': 'MO3 + G'},
    {'display': 'F5',  'name': 'F5',  'keys': [curses.KEY_F5],  'layer': 3, 'hint': 'MO3 + N'},
    {'display': 'F6',  'name': 'F6',  'keys': [curses.KEY_F6],  'layer': 3, 'hint': 'MO3 + M'},
    {'display': 'F7',  'name': 'F7',  'keys': [curses.KEY_F7],  'layer': 3, 'hint': 'MO3 + ,'},
    {'display': 'F8',  'name': 'F8',  'keys': [curses.KEY_F8],  'layer': 3, 'hint': 'MO3 + .'},
    {'display': 'F9',  'name': 'F9',  'keys': [curses.KEY_F9],  'layer': 3, 'hint': 'MO3 + K'},
    {'display': 'F10', 'name': 'F10', 'keys': [curses.KEY_F10], 'layer': 3, 'hint': 'MO3 + L'},
    {'display': 'F11', 'name': 'F11', 'keys': [curses.KEY_F11], 'layer': 3, 'hint': 'MO3 + ;'},
    {'display': 'F12', 'name': 'F12', 'keys': [curses.KEY_F12], 'layer': 3, 'hint': "MO3 + '"},
]

LAYER_COLORS = {1: 4, 2: 3, 3: 5}   # L1=cyan, L2=yellow, L3=magenta
FILTER_CYCLE = ['all', 'l1', 'l2', 'l3']
FILTER_LABELS = {'all': 'All Layers', 'l1': 'L1 Nav only', 'l2': 'L2 Sym only', 'l3': 'L3 Fn only'}


def build_pool(filter_key):
    layer_map = {'all': None, 'l1': 1, 'l2': 2, 'l3': 3}
    layer = layer_map[filter_key]
    pool = [c for c in KEY_CHALLENGES if layer is None or c['layer'] == layer]
    if not pool:
        pool = KEY_CHALLENGES[:]
    random.shuffle(pool)
    return pool


# ── MAIN GAME ─────────────────────────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_GREEN, -1)    # correct
    curses.init_pair(2, curses.COLOR_RED, -1)       # wrong
    curses.init_pair(3, curses.COLOR_YELLOW, -1)    # pending / mode highlight
    curses.init_pair(4, curses.COLOR_CYAN, -1)      # info / layer1
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)   # accent / mixed
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)  # selected mode
    curses.init_pair(7, curses.COLOR_WHITE, -1)     # normal
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN)  # correct bg
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_RED)    # wrong bg
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_CYAN)  # cursor
    curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_GREEN)   # flash correct
    curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_RED)     # flash wrong
    curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_MAGENTA) # flash L3

    mode = 0
    state = new_state(mode)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        if w < 60 or h < 20:
            stdscr.addstr(0, 0, "Terminal too small! Please resize to at least 60x20.")
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('q'):
                break
            continue

        draw_ui(stdscr, state, mode, h, w)
        stdscr.refresh()

        stdscr.nodelay(True)
        key = stdscr.getch()

        if key == -1:
            if mode == 4:
                # Auto-advance after correct
                if (state['feedback'] == 'correct' and state['feedback_time'] and
                        time.time() - state['feedback_time'] > 0.6):
                    advance_flash(state)
            elif state['started'] and not state['finished']:
                elapsed = time.time() - state['start_time']
                state['time_left'] = max(0, 30 - int(elapsed))
                if state['time_left'] == 0:
                    state['finished'] = True
            time.sleep(0.05)
            continue

        stdscr.nodelay(False)

        # Global keys
        if key == ord('q') or key == 27:  # q or ESC
            if state['finished']:
                state = new_state(mode)
            else:
                break
        elif key == ord('1'):
            mode = 0; state = new_state(mode)
        elif key == ord('2'):
            mode = 1; state = new_state(mode)
        elif key == ord('3'):
            mode = 2; state = new_state(mode)
        elif key == ord('4'):
            mode = 3; state = new_state(mode)
        elif key == ord('5'):
            mode = 4; state = new_state(mode)
        elif key == ord('\t'):  # Tab = next mode
            mode = (mode + 1) % 5; state = new_state(mode)
        elif key == ord('r'):
            state = new_state(mode)
        elif mode == 4:
            handle_key_flash(state, key)
        elif not state['finished']:
            handle_keypress(state, key, mode)


# ── STATE FACTORIES ───────────────────────────────────────────────────────────

def new_state(mode):
    if mode == 4:
        return new_flash_state()
    return {
        'mode': mode,
        'text': random.choice(WORDS[mode]),
        'typed': '',
        'started': False,
        'finished': False,
        'start_time': None,
        'time_left': 30,
        'total_chars': 0,
        'wrong_chars': 0,
        'streak': 0,
        'best_streak': 0,
        'wpm': 0,
        'accuracy': 100,
    }


def new_flash_state(filter_key='all'):
    pool = build_pool(filter_key)
    return {
        'mode': 4,
        'filter': filter_key,
        'pool': pool,
        'pool_idx': 0,
        'challenge': pool[0],
        'hint_shown': False,
        'feedback': None,       # None / 'correct' / 'wrong'
        'feedback_time': None,
        'wrong_this': 0,        # wrong attempts on current challenge
        'total_done': 0,
        'correct_first': 0,
        'streak': 0,
        'best_streak': 0,
        'accuracy': 100,
        # compat fields (not used but keeps draw_ui safe)
        'started': False,
        'finished': False,
        'start_time': None,
        'time_left': 0,
        'wpm': 0,
    }


def advance_flash(state):
    state['pool_idx'] += 1
    if state['pool_idx'] >= len(state['pool']):
        state['pool_idx'] = 0
        random.shuffle(state['pool'])
    state['challenge'] = state['pool'][state['pool_idx']]
    state['hint_shown'] = False
    state['feedback'] = None
    state['feedback_time'] = None
    state['wrong_this'] = 0


# ── KEY HANDLERS ──────────────────────────────────────────────────────────────

def handle_keypress(state, key, mode):
    if state['finished']:
        return

    if key in (curses.KEY_BACKSPACE, 127, 8):
        if state['typed']:
            state['typed'] = state['typed'][:-1]
        return

    if 32 <= key <= 126:
        char = chr(key)

        if not state['started']:
            state['started'] = True
            state['start_time'] = time.time()

        if len(state['typed']) < len(state['text']):
            expected = state['text'][len(state['typed'])]
            state['typed'] += char
            state['total_chars'] += 1

            if char == expected:
                state['streak'] += 1
                if state['streak'] > state['best_streak']:
                    state['best_streak'] = state['streak']
            else:
                state['wrong_chars'] += 1
                state['streak'] = 0

            if state['started']:
                elapsed = max(0.1, time.time() - state['start_time'])
                words = state['total_chars'] / 5
                state['wpm'] = int(words / (elapsed / 60))
                correct = state['total_chars'] - state['wrong_chars']
                state['accuracy'] = int((correct / state['total_chars']) * 100) if state['total_chars'] > 0 else 100

            if len(state['typed']) >= len(state['text']):
                state['text'] = random.choice(WORDS[mode])
                state['typed'] = ''


def handle_key_flash(state, key):
    # h = show hint early
    if key == ord('h'):
        state['hint_shown'] = True
        return

    # f = cycle layer filter
    if key == ord('f'):
        idx = FILTER_CYCLE.index(state['filter'])
        new_filter = FILTER_CYCLE[(idx + 1) % len(FILTER_CYCLE)]
        saved_done = state['total_done']
        saved_correct = state['correct_first']
        saved_streak = state['streak']
        saved_best = state['best_streak']
        state.update(new_flash_state(new_filter))
        state['total_done'] = saved_done
        state['correct_first'] = saved_correct
        state['streak'] = saved_streak
        state['best_streak'] = saved_best
        return

    # Waiting for auto-advance after correct — ignore input
    if state['feedback'] == 'correct':
        return

    challenge = state['challenge']

    if key in challenge['keys']:
        state['feedback'] = 'correct'
        state['feedback_time'] = time.time()
        state['total_done'] += 1
        if state['wrong_this'] == 0:
            state['correct_first'] += 1
            state['streak'] += 1
            if state['streak'] > state['best_streak']:
                state['best_streak'] = state['streak']
        else:
            state['streak'] = 0
        if state['total_done'] > 0:
            state['accuracy'] = int(state['correct_first'] / state['total_done'] * 100)
    else:
        state['feedback'] = 'wrong'
        state['feedback_time'] = time.time()
        state['wrong_this'] += 1
        state['hint_shown'] = True


# ── DRAWING ───────────────────────────────────────────────────────────────────

def draw_ui(stdscr, state, mode, h, w):
    if mode == 4:
        draw_flash_header(stdscr, state, mode, h, w)
        draw_key_flash(stdscr, state, h, w)
        return

    mc = MODE_COLORS[mode]

    # ── HEADER ──
    title = "SILAKKA54 TRAINER"
    stdscr.attron(curses.color_pair(mc) | curses.A_BOLD)
    stdscr.addstr(0, (w - len(title)) // 2, title)
    stdscr.attroff(curses.color_pair(mc) | curses.A_BOLD)

    # ── MODE TABS ──
    draw_tabs(stdscr, mode, w, row=2)

    # ── MODE DESC ──
    desc = MODE_DESCS[mode]
    if len(desc) < w - 4:
        stdscr.addstr(3, 2, desc[:w-4], curses.color_pair(mc) | curses.A_DIM)

    # ── DIVIDER ──
    stdscr.addstr(4, 0, "─" * w, curses.color_pair(7) | curses.A_DIM)

    # ── STATS BAR ──
    timer_color = curses.color_pair(2) if state['time_left'] <= 5 else (
        curses.color_pair(3) if state['time_left'] <= 10 else curses.color_pair(7))

    stats = [
        ("WPM",    f"{state['wpm']:>4}",          curses.color_pair(mc) | curses.A_BOLD),
        ("ACC",    f"{state['accuracy']:>3}%",     curses.color_pair(1) | curses.A_BOLD),
        ("STREAK", f"{state['streak']:>4}",        curses.color_pair(3) | curses.A_BOLD),
        ("BEST",   f"{state['best_streak']:>4}",   curses.color_pair(5) | curses.A_BOLD),
        ("TIME",   f"{state['time_left']:>3}s",    timer_color | curses.A_BOLD),
    ]

    sx = 2
    for label, val, attr in stats:
        stdscr.addstr(5, sx, label + ": ", curses.color_pair(7) | curses.A_DIM)
        sx += len(label) + 2
        stdscr.attron(attr)
        stdscr.addstr(5, sx, val)
        stdscr.attroff(attr)
        sx += len(val) + 4

    # Progress bar
    if state['started']:
        elapsed = time.time() - state['start_time']
        progress = min(1.0, elapsed / 30)
        bar_w = w - 4
        filled = int(bar_w * progress)
        bar = "█" * filled + "░" * (bar_w - filled)
        stdscr.addstr(6, 2, bar[:bar_w], curses.color_pair(mc) | curses.A_DIM)

    stdscr.addstr(7, 0, "─" * w, curses.color_pair(7) | curses.A_DIM)

    # ── TYPING AREA ──
    text = state['text']
    typed = state['typed']
    ty = 9
    tx = 2
    max_line = w - 4

    lines = []
    current_line = ""
    for i, ch in enumerate(text):
        current_line += ch
        if len(current_line) >= max_line:
            lines.append(current_line)
            current_line = ""
    if current_line:
        lines.append(current_line)

    char_idx = 0
    for line in lines:
        cx = tx
        for ch in line:
            display = ch if ch != ' ' else '·'
            if char_idx < len(typed):
                if typed[char_idx] == text[char_idx]:
                    attr = curses.color_pair(1) | curses.A_BOLD
                else:
                    attr = curses.color_pair(9) | curses.A_BOLD
                    display = text[char_idx] if text[char_idx] != ' ' else '·'
            elif char_idx == len(typed):
                attr = curses.color_pair(10) | curses.A_BOLD
            else:
                attr = curses.color_pair(7) | curses.A_DIM

            try:
                stdscr.addstr(ty, cx, display, attr)
            except curses.error:
                pass
            cx += 1
            char_idx += 1
        ty += 1

    # ── HINT LINE ──
    hint_y = ty + 1
    if len(typed) < len(text):
        next_char = text[len(typed)]
        hint = get_hint(next_char)
        if hint:
            stdscr.addstr(hint_y, 2, f"hint: {hint}", curses.color_pair(3) | curses.A_BOLD)
        else:
            stdscr.addstr(hint_y, 2, " " * 30)
    else:
        stdscr.addstr(hint_y, 2, "  done! loading next...", curses.color_pair(1))

    if state['finished']:
        draw_results(stdscr, state, h, w, mc)
        return

    footer_y = h - 1
    controls = " [r]restart  [tab]next mode  [1-5]mode  [q]quit "
    try:
        stdscr.addstr(footer_y, 0, controls[:w], curses.color_pair(7) | curses.A_DIM | curses.A_REVERSE)
    except curses.error:
        pass


def draw_tabs(stdscr, mode, w, row=2):
    stdscr.addstr(row, 2, "MODE: ", curses.color_pair(7))
    tab_x = 8
    for m, name in MODE_NAMES.items():
        label = f" [{m+1}]{name} "
        if m == mode:
            stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
            stdscr.addstr(row, tab_x, label)
            stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
        else:
            stdscr.addstr(row, tab_x, label, curses.color_pair(7) | curses.A_DIM)
        tab_x += len(label) + 1


def draw_flash_header(stdscr, state, mode, h, w):
    mc = MODE_COLORS[mode]
    title = "SILAKKA54 TRAINER"
    stdscr.attron(curses.color_pair(mc) | curses.A_BOLD)
    stdscr.addstr(0, (w - len(title)) // 2, title)
    stdscr.attroff(curses.color_pair(mc) | curses.A_BOLD)
    draw_tabs(stdscr, mode, w, row=2)
    desc = MODE_DESCS[mode]
    stdscr.addstr(3, 2, desc[:w-4], curses.color_pair(mc) | curses.A_DIM)
    stdscr.addstr(4, 0, "─" * w, curses.color_pair(7) | curses.A_DIM)


def draw_key_flash(stdscr, state, h, w):
    challenge = state['challenge']
    layer = challenge['layer']
    lc = LAYER_COLORS.get(layer, 7)
    feedback = state['feedback']

    # ── STATS ROW ──
    acc_color = curses.color_pair(1) if state['accuracy'] >= 80 else (
        curses.color_pair(3) if state['accuracy'] >= 60 else curses.color_pair(2))
    stats = [
        ("DONE",   f"{state['total_done']:>4}",        curses.color_pair(lc) | curses.A_BOLD),
        ("1ST-TRY", f"{state['correct_first']:>4}",    curses.color_pair(1) | curses.A_BOLD),
        ("ACC",    f"{state['accuracy']:>3}%",          acc_color | curses.A_BOLD),
        ("STREAK", f"{state['streak']:>4}",             curses.color_pair(3) | curses.A_BOLD),
        ("BEST",   f"{state['best_streak']:>4}",        curses.color_pair(5) | curses.A_BOLD),
        ("FILTER", FILTER_LABELS[state['filter']],      curses.color_pair(4) | curses.A_BOLD),
    ]
    sx = 2
    for label, val, attr in stats:
        stdscr.addstr(5, sx, label + ": ", curses.color_pair(7) | curses.A_DIM)
        sx += len(label) + 2
        try:
            stdscr.attron(attr)
            stdscr.addstr(5, sx, val)
            stdscr.attroff(attr)
        except curses.error:
            pass
        sx += len(val) + 3

    stdscr.addstr(6, 0, "─" * w, curses.color_pair(7) | curses.A_DIM)

    # ── BIG CHARACTER BOX ──
    display = challenge['display']
    name = challenge['name']
    layer_badge = f"L{layer}"

    box_w = 32
    box_h = 9
    box_y = max(8, h // 2 - box_h // 2)
    box_x = (w - box_w) // 2

    if feedback == 'correct':
        border_attr = curses.color_pair(1) | curses.A_BOLD
        char_attr   = curses.color_pair(1) | curses.A_BOLD
    elif feedback == 'wrong':
        border_attr = curses.color_pair(2) | curses.A_BOLD
        char_attr   = curses.color_pair(2) | curses.A_BOLD
    else:
        border_attr = curses.color_pair(lc) | curses.A_BOLD
        char_attr   = curses.color_pair(lc) | curses.A_BOLD

    # Draw box
    try:
        stdscr.addstr(box_y,           box_x, "╔" + "═" * (box_w - 2) + "╗", border_attr)
        stdscr.addstr(box_y + box_h - 2, box_x, "╟" + "─" * (box_w - 2) + "╢", border_attr)
        stdscr.addstr(box_y + box_h - 1, box_x, "╚" + "═" * (box_w - 2) + "╝", border_attr)
        for y in range(box_y + 1, box_y + box_h - 2):
            stdscr.addstr(y, box_x,           "║", border_attr)
            stdscr.addstr(y, box_x + box_w - 1, "║", border_attr)
        stdscr.addstr(box_y + box_h - 1, box_x, "║", border_attr)
        stdscr.addstr(box_y + box_h - 1, box_x + box_w - 1, "║", border_attr)
    except curses.error:
        pass

    # Big character (centered vertically in box body)
    char_y = box_y + (box_h - 2) // 2
    char_x = box_x + (box_w - len(display)) // 2
    try:
        stdscr.addstr(char_y, char_x, display, char_attr | curses.A_BOLD)
    except curses.error:
        pass

    # Label row: "L2 · Open Brace"
    label_str = f" {layer_badge} · {name} "
    label_x = box_x + max(1, (box_w - len(label_str)) // 2)
    try:
        stdscr.addstr(box_y + box_h - 1, label_x, label_str[:box_w - 2], curses.color_pair(lc))
    except curses.error:
        pass

    # ── STATUS & HINT ──
    status_y = box_y + box_h + 1
    hint_y   = box_y + box_h + 3

    if feedback == 'correct':
        msg = "✓  CORRECT!"
        mx = (w - len(msg)) // 2
        try:
            stdscr.addstr(status_y, mx, msg, curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass
    elif feedback == 'wrong':
        msg = "✗  Wrong — try again"
        mx = (w - len(msg)) // 2
        try:
            stdscr.addstr(status_y, mx, msg, curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass

    if state['hint_shown']:
        hint_str = f"  hint: {challenge['hint']}  "
        hx = (w - len(hint_str)) // 2
        try:
            stdscr.addstr(hint_y, hx, hint_str, curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass
    elif feedback is None:
        tip = "[h] reveal hint"
        try:
            stdscr.addstr(hint_y, (w - len(tip)) // 2, tip, curses.color_pair(7) | curses.A_DIM)
        except curses.error:
            pass

    # ── FOOTER ──
    footer_y = h - 1
    controls = " [h]hint  [f]filter layer  [r]reset  [tab]mode  [1-5]mode  [q]quit "
    try:
        stdscr.addstr(footer_y, 0, controls[:w], curses.color_pair(7) | curses.A_DIM | curses.A_REVERSE)
    except curses.error:
        pass


def draw_results(stdscr, state, h, w, mc):
    box_h, box_w = 14, 44
    box_y = (h - box_h) // 2
    box_x = (w - box_w) // 2

    for y in range(box_y, box_y + box_h):
        try:
            stdscr.addstr(y, box_x, " " * box_w, curses.color_pair(6))
        except curses.error:
            pass

    try:
        stdscr.addstr(box_y, box_x, "╔" + "═" * (box_w - 2) + "╗", curses.color_pair(mc) | curses.A_BOLD)
        stdscr.addstr(box_y + box_h - 1, box_x, "╚" + "═" * (box_w - 2) + "╝", curses.color_pair(mc) | curses.A_BOLD)
        for y in range(box_y + 1, box_y + box_h - 1):
            stdscr.addstr(y, box_x, "║", curses.color_pair(mc) | curses.A_BOLD)
            stdscr.addstr(y, box_x + box_w - 1, "║", curses.color_pair(mc) | curses.A_BOLD)
    except curses.error:
        pass

    def center_in_box(y, text, attr):
        px = box_x + (box_w - len(text)) // 2
        try:
            stdscr.addstr(y, px, text, attr)
        except curses.error:
            pass

    center_in_box(box_y + 2, "ROUND COMPLETE!", curses.color_pair(mc) | curses.A_BOLD)
    center_in_box(box_y + 3, "─" * 24, curses.color_pair(7) | curses.A_DIM)

    center_in_box(box_y + 5, f"WPM      {state['wpm']:>5}", curses.color_pair(mc) | curses.A_BOLD)
    center_in_box(box_y + 6, f"Accuracy {state['accuracy']:>4}%", curses.color_pair(1) | curses.A_BOLD)
    center_in_box(box_y + 7, f"Streak   {state['best_streak']:>5}", curses.color_pair(3) | curses.A_BOLD)
    center_in_box(box_y + 8, f"Errors   {state['wrong_chars']:>5}", curses.color_pair(2) | curses.A_BOLD)

    wpm = state['wpm']
    if wpm >= 60:
        grade, gcol = "EXCELLENT ★★★", curses.color_pair(1)
    elif wpm >= 40:
        grade, gcol = "GOOD      ★★☆", curses.color_pair(3)
    elif wpm >= 20:
        grade, gcol = "LEARNING  ★☆☆", curses.color_pair(mc)
    else:
        grade, gcol = "KEEP GOING ☆☆☆", curses.color_pair(7)

    center_in_box(box_y + 10, grade, gcol | curses.A_BOLD)
    center_in_box(box_y + 12, "[ r ] retry   [ tab ] next mode   [ q ] quit", curses.color_pair(7) | curses.A_DIM)


# ── ENTRY ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("\nGood practice! Keep at it 💪")
