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
QWidget[transparent="true"] {{ background: transparent; }}
QLabel[role="muted"] {{ color: {MUTED}; }}
QLabel[role="title"] {{ font-size: 32px; font-weight: 700; }}
QLabel[role="subtitle"] {{ color: {MUTED}; font-size: 17px; }}
QLabel[role="heading"] {{ font-size: 17px; font-weight: 600; }}
QLabel[role="error"] {{ color: {DANGER}; }}
QLabel[role="notice"] {{
    color: {SUCCESS};
    background: {SUCCESS_SOFT};
    border: 1px solid {SUCCESS};
    border-radius: 10px;
    padding: 10px 16px;
}}
QLabel[role="label"] {{ color: {MUTED}; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }}
QLabel[role="privacyTag"] {{
    color: {SUCCESS};
    background: {SUCCESS_SOFT};
    border: 1px solid {SUCCESS};
    border-radius: 10px;
    padding: 1px 10px;
    font-size: 12px;
}}

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

QPushButton[option="true"]:checked {{
    background: {ACCENT_SOFT};
    border-color: {ACCENT};
    color: {ACCENT_TEXT};
}}

QCheckBox {{ background: transparent; spacing: 8px; }}

QSplitter::handle {{ background: transparent; height: 12px; }}

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
QPushButton[tag="true"] {{
    background: {ACCENT_SOFT};
    color: {ACCENT_TEXT};
    border: 1px solid transparent;
    border-radius: 12px;
    padding: 3px 12px;
    font-size: 13px;
    font-weight: 400;
}}
QPushButton[tag="true"]:hover {{ border-color: {ACCENT}; }}
QPushButton[tag="true"]:checked {{
    background: {ACCENT};
    color: {PAGE_BG};
    border-color: {ACCENT};
}}

QComboBox {{
    background: {PAGE_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 10px;
}}
QComboBox QAbstractItemView {{ background: {SURFACE_RAISED}; selection-background-color: {ACCENT_SOFT}; }}

QTableView {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    gridline-color: {BORDER};
    font-size: 13px;
}}
QHeaderView {{ background: {SURFACE}; border: none; }}
QHeaderView::section {{
    background: {SURFACE_RAISED};
    color: {TEXT};
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid {BORDER};
    padding: 6px 10px;
    font-weight: 600;
}}
QHeaderView::section:vertical {{ color: {MUTED}; font-weight: 400; padding: 0 8px; }}
QTableCornerButton::section {{ background: {SURFACE_RAISED}; border: none; }}

QScrollBar:vertical, QScrollBar:horizontal {{ background: {SURFACE}; border: none; width: 10px; height: 10px; }}
QScrollBar::handle {{ background: {BORDER}; border-radius: 5px; min-height: 30px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
"""
