"""Dark theme with the same palette as the web version (and the portfolio)."""

PAGE_BG = "#0d1117"
SURFACE = "#161b22"
SURFACE_RAISED = "#21262d"
BORDER = "#30363d"
TEXT = "#e6edf3"
BTN_TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
ACCENT_SOFT = "#1a2740"
ACCENT_TEXT = "#79c0ff"
SUCCESS = "#3fb950"
SUCCESS_SOFT = "#12261e"
WARNING = "#d29922"
WARNING_SOFT = "#2b2111"
DANGER = "#f85149"

STYLESHEET = f"""
QWidget {{
    background: {PAGE_BG};
    color: {TEXT};
    font-size: 14px;
}}
QLabel {{ background: transparent; }}
QLabel[role="muted"] {{ color: {MUTED}; }}
QLabel[role="title"] {{ font-size: 32px; font-weight: 700; }}
QLabel[role="subtitle"] {{ color: {MUTED}; font-size: 17px; }}
QLabel[role="heading"] {{ font-size: 17px; font-weight: 600; }}
QLabel[role="error"] {{ color: {DANGER}; }}

QFrame#card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

QFrame#callout {{
    background: {SUCCESS_SOFT};
    border: 1px solid {SUCCESS};
    border-radius: 10px;
}}
QFrame#callout QLabel {{ color: {TEXT}; }}
QFrame#callout QLabel[role="calloutTitle"] {{ color: {SUCCESS}; font-weight: 600; }}

QFrame#dropZone {{
    background: {PAGE_BG};
    border: 1px dashed {BORDER};
    border-radius: 10px;
}}
QFrame#dropZone[dragging="true"] {{
    background: {ACCENT_SOFT};
    border-color: {ACCENT};
}}

QPushButton {{
    background: {SURFACE_RAISED};
    color: {BTN_TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}}
QPushButton:hover {{ background: {BORDER}; border-color: {MUTED}; }}
QPushButton:disabled {{ color: {MUTED}; }}
QPushButton[primary="true"] {{
    background: {ACCENT};
    color: {PAGE_BG};
    border-color: {ACCENT};
}}
QPushButton[primary="true"]:hover {{ background: {ACCENT_TEXT}; border-color: {ACCENT_TEXT}; }}

QPushButton[lang="true"] {{
    background: transparent;
    border: none;
    color: {MUTED};
    padding: 2px 8px;
}}
QPushButton[lang="true"]:checked {{
    background: {SURFACE_RAISED};
    color: {TEXT};
    font-weight: 700;
    border-radius: 4px;
}}
"""
