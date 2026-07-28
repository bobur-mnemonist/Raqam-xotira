import json
import os
import random
import time
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.lang import Builder

Window.clearcolor = (0.04, 0.04, 0.043, 1)  # near-black bg

DATA_FILE = os.path.join(App.get_running_app().user_data_dir if App.get_running_app() else ".", "sessions.json") \
    if False else "sessions.json"


def data_path():
    app = App.get_running_app()
    if app:
        return os.path.join(app.user_data_dir, "sessions.json")
    return "sessions.json"


def load_sessions():
    path = data_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_sessions(sessions):
    path = data_path()
    try:
        with open(path, "w") as f:
            json.dump(sessions, f)
    except Exception as e:
        print("Save error:", e)


def gen_digits(n):
    return "".join(str(random.randint(0, 9)) for _ in range(n))


def group_digits(s, size=5):
    return " ".join(s[i:i + size] for i in range(0, len(s), size))


def fmt_time(sec):
    m = sec // 60
    s = sec % 60
    return f"{m}:{s:02d}"


KV = """
#:import dp kivy.metrics.dp

<AccentButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    color: 0.04, 0.04, 0.043, 1
    bold: True
    font_size: '18sp'
    canvas.before:
        Color:
            rgba: (0.769, 0.945, 0.208, 1) if self.state == "normal" else (0.6, 0.75, 0.16, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(4)]

<GhostButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    color: 0.769, 0.945, 0.208, 1
    bold: True
    font_size: '16sp'
    canvas.before:
        Color:
            rgba: (0.769, 0.945, 0.208, 1) if self.state == "down" else (0,0,0,0)
        Line:
            width: 1.4
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(4))

<ChipButton@ToggleButton>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    bold: True
    font_size: '15sp'
    color: (0.04,0.04,0.043,1) if self.state == "down" else (0.769, 0.945, 0.208, 1)
    canvas.before:
        Color:
            rgba: (0.769, 0.945, 0.208, 1) if self.state == "down" else (0,0,0,0)
        Line:
            width: 1.2
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(4))
"""
Builder.load_string(KV)


class SetupScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.digit_count = 100
        self.mem_time = 300
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(18))

        eyebrow = Label(
            text="PAO 100 * SPEED NUMBERS",
            color=(0.769, 0.945, 0.208, 1),
            font_size="13sp",
            bold=True,
            size_hint_y=None,
            height=dp(24),
            halign="left",
        )
        eyebrow.bind(size=eyebrow.setter("text_size"))
        title = Label(
            text="Raqamlar xotira mashqi",
            color=(0.93, 0.93, 0.92, 1),
            font_size="26sp",
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign="left",
        )
        title.bind(size=title.setter("text_size"))

        root.add_widget(eyebrow)
        root.add_widget(title)

        # Digit count selector
        root.add_widget(self._section_label("RAQAMLAR SONI"))
        count_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.count_buttons = {}
        for n in (50, 100, 150, 200):
            b = Builder.load_string("ChipButton:")
            b.text = str(n)
            b.group = "count"
            b.state = "down" if n == self.digit_count else "normal"
            b.bind(on_press=lambda inst, val=n: self.set_count(val))
            self.count_buttons[n] = b
            count_row.add_widget(b)
        root.add_widget(count_row)

        # Custom count input
        custom_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.custom_input = TextInput(
            hint_text="boshqa son...",
            multiline=False,
            input_filter="int",
            background_color=(0.09, 0.1, 0.11, 1),
            foreground_color=(0.93, 0.93, 0.92, 1),
            cursor_color=(0.769, 0.945, 0.208, 1),
            padding=[dp(10), dp(12)],
            font_size="15sp",
        )
        self.custom_input.bind(text=self.on_custom_count)
        custom_row.add_widget(self.custom_input)
        root.add_widget(custom_row)

        # Time selector
        root.add_widget(self._section_label("YODLASH VAQTI"))
        time_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        for label, secs in (("1:00", 60), ("3:00", 180), ("5:00", 300), ("10:00", 600)):
            b = Builder.load_string("ChipButton:")
            b.text = label
            b.group = "time"
            b.state = "down" if secs == self.mem_time else "normal"
            b.bind(on_press=lambda inst, val=secs: self.set_time(val))
            time_row.add_widget(b)
        root.add_widget(time_row)

        root.add_widget(BoxLayout())  # spacer

        start_btn = Builder.load_string("AccentButton:")
        start_btn.text = "BOSHLASH"
        start_btn.size_hint_y = None
        start_btn.height = dp(56)
        start_btn.bind(on_press=self.start_session)
        root.add_widget(start_btn)

        nav_btn = Builder.load_string("GhostButton:")
        nav_btn.text = "Jurnal"
        nav_btn.size_hint_y = None
        nav_btn.height = dp(48)
        nav_btn.bind(on_press=lambda *a: setattr(self.manager, "current", "log"))
        root.add_widget(nav_btn)

        self.add_widget(root)

    def _section_label(self, text):
        lbl = Label(
            text=text,
            color=(0.55, 0.55, 0.56, 1),
            font_size="12sp",
            bold=True,
            size_hint_y=None,
            height=dp(20),
            halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def set_count(self, val):
        self.digit_count = val
        self.custom_input.text = ""

    def on_custom_count(self, instance, value):
        if value.strip():
            try:
                self.digit_count = int(value)
                for n, b in self.count_buttons.items():
                    b.state = "normal"
            except ValueError:
                pass

    def set_time(self, val):
        self.mem_time = val

    def start_session(self, *args):
        if self.digit_count < 10:
            self.digit_count = 10
        mem_screen = self.manager.get_screen("memorize")
        mem_screen.setup(self.digit_count, self.mem_time)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "memorize"


class MemorizeScreen(Screen):
    def setup(self, digit_count, mem_time):
        self.digit_count = digit_count
        self.mem_time = mem_time
        self.time_left = mem_time
        self.digits = gen_digits(digit_count)
        self.build_ui()
        self._event = Clock.schedule_interval(self.tick, 1)

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(14))

        top_row = BoxLayout(size_hint_y=None, height=dp(36))
        lbl = Label(
            text=f"YODLASH - {self.digit_count} RAQAM",
            color=(0.55, 0.55, 0.56, 1),
            font_size="13sp",
            bold=True,
            halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.timer_label = Label(
            text=fmt_time(self.time_left),
            color=(0.769, 0.945, 0.208, 1),
            font_size="24sp",
            bold=True,
            halign="right",
        )
        self.timer_label.bind(size=self.timer_label.setter("text_size"))
        top_row.add_widget(lbl)
        top_row.add_widget(self.timer_label)
        root.add_widget(top_row)

        scroll = ScrollView()
        self.digits_label = Label(
            text=group_digits(self.digits),
            color=(0.93, 0.93, 0.92, 1),
            font_size="24sp",
            bold=True,
            size_hint_y=None,
            halign="left",
            valign="top",
            line_height=1.6,
        )
        self.digits_label.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None)),
            texture_size=lambda inst, ts: setattr(inst, "height", ts[1]),
        )
        scroll.add_widget(self.digits_label)
        root.add_widget(scroll)

        stop_btn = Builder.load_string("GhostButton:")
        stop_btn.text = "Erta tugatish -> Yozib berish"
        stop_btn.size_hint_y = None
        stop_btn.height = dp(52)
        stop_btn.bind(on_press=self.finish_early)
        root.add_widget(stop_btn)

        self.add_widget(root)

    def tick(self, dt):
        self.time_left -= 1
        if self.time_left <= 0:
            self.timer_label.text = "0:00"
            self._event.cancel()
            self.go_recall()
        else:
            self.timer_label.text = fmt_time(self.time_left)
            if self.time_left <= 10:
                self.timer_label.color = (0.85, 0.33, 0.29, 1)

    def finish_early(self, *args):
        self._event.cancel()
        self.go_recall()

    def go_recall(self):
        recall_screen = self.manager.get_screen("recall")
        recall_screen.setup(self.digits, self.digit_count, self.mem_time)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "recall"


class RecallScreen(Screen):
    def setup(self, digits, digit_count, mem_time):
        self.digits = digits
        self.digit_count = digit_count
        self.mem_time = mem_time
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(14))

        lbl = Label(
            text=f"ESLASH - {self.digit_count} ta raqamni tering",
            color=(0.55, 0.55, 0.56, 1),
            font_size="13sp",
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        root.add_widget(lbl)

        self.input_box = TextInput(
            hint_text="Raqamlarni shu yerga tering...",
            multiline=True,
            input_filter=self._digit_filter,
            background_color=(0.09, 0.1, 0.11, 1),
            foreground_color=(0.93, 0.93, 0.92, 1),
            cursor_color=(0.769, 0.945, 0.208, 1),
            font_size="20sp",
            padding=[dp(12), dp(12)],
        )
        self.input_box.bind(text=self.update_count)
        root.add_widget(self.input_box)

        self.count_label = Label(
            text=f"Kiritilgan: 0 / {self.digit_count}",
            color=(0.55, 0.55, 0.56, 1),
            font_size="13sp",
            size_hint_y=None,
            height=dp(24),
            halign="left",
        )
        self.count_label.bind(size=self.count_label.setter("text_size"))
        root.add_widget(self.count_label)

        check_btn = Builder.load_string("AccentButton:")
        check_btn.text = "TEKSHIRISH"
        check_btn.size_hint_y = None
        check_btn.height = dp(56)
        check_btn.bind(on_press=self.check)
        root.add_widget(check_btn)

        self.add_widget(root)

    def _digit_filter(self, text, from_undo):
        return "".join(c for c in text if c.isdigit())

    def update_count(self, instance, value):
        cleaned = "".join(c for c in value if c.isdigit())
        self.count_label.text = f"Kiritilgan: {len(cleaned)} / {self.digit_count}"

    def check(self, *args):
        cleaned = "".join(c for c in self.input_box.text if c.isdigit())
        correct = 0
        errors = 0
        for i, d in enumerate(self.digits):
            if i >= len(cleaned):
                continue
            if cleaned[i] == d:
                correct += 1
            else:
                errors += 1
        blank = max(0, len(self.digits) - len(cleaned))

        result = {
            "id": int(time.time() * 1000),
            "date": datetime.now().isoformat(),
            "total": self.digit_count,
            "mem_time": self.mem_time,
            "correct": correct,
            "errors": errors,
            "blank": blank,
        }
        sessions = load_sessions()
        sessions.insert(0, result)
        save_sessions(sessions[:200])

        result_screen = self.manager.get_screen("result")
        result_screen.setup(self.digits, cleaned, result)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "result"


class ResultScreen(Screen):
    def setup(self, digits, entered, result):
        self.digits = digits
        self.entered = entered
        self.result = result
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(14))

        stats_row = BoxLayout(size_hint_y=None, height=dp(90), spacing=dp(10))
        stats_row.add_widget(self._stat_card("TO'G'RI", str(self.result["correct"]), (0.29, 0.49, 0.49, 1)))
        stats_row.add_widget(self._stat_card("XATO", str(self.result["errors"]), (0.71, 0.33, 0.29, 1)))
        stats_row.add_widget(self._stat_card("BO'SH", str(self.result["blank"]), (0.55, 0.55, 0.56, 1)))
        root.add_widget(stats_row)

        scroll = ScrollView()
        detail_text = ""
        entered = self.entered
        markup_parts = []
        for i, d in enumerate(self.digits):
            if i >= len(entered):
                markup_parts.append(f"[color=8c8f96]{d}[/color]")
            elif entered[i] == d:
                markup_parts.append(f"[color=4a7c7c]{d}[/color]")
            else:
                markup_parts.append(f"[color=b5544a]{d}[/color]")
        detail_text = "".join(markup_parts)

        detail_label = Label(
            text=detail_text,
            markup=True,
            font_size="16sp",
            size_hint_y=None,
            halign="left",
            valign="top",
            line_height=1.7,
        )
        detail_label.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None)),
            texture_size=lambda inst, ts: setattr(inst, "height", ts[1]),
        )
        scroll.add_widget(detail_label)
        root.add_widget(scroll)

        new_btn = Builder.load_string("AccentButton:")
        new_btn.text = "YANGI MASHQ"
        new_btn.size_hint_y = None
        new_btn.height = dp(56)
        new_btn.bind(on_press=lambda *a: setattr(self.manager, "current", "setup"))
        root.add_widget(new_btn)

        log_btn = Builder.load_string("GhostButton:")
        log_btn.text = "Jurnalni ko'rish"
        log_btn.size_hint_y = None
        log_btn.height = dp(48)
        log_btn.bind(on_press=lambda *a: setattr(self.manager, "current", "log"))
        root.add_widget(log_btn)

        self.add_widget(root)

    def _stat_card(self, label, value, color):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(4))
        with box.canvas.before:
            Color(0.09, 0.1, 0.11, 1)
            box._bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(6)])
        box.bind(
            pos=lambda inst, val: setattr(inst._bg, "pos", val),
            size=lambda inst, val: setattr(inst._bg, "size", val),
        )
        lbl1 = Label(text=label, color=(0.55, 0.55, 0.56, 1), font_size="11sp", bold=True, size_hint_y=None, height=dp(18))
        lbl2 = Label(text=value, color=color, font_size="24sp", bold=True)
        box.add_widget(lbl1)
        box.add_widget(lbl2)
        return box


class LogScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        sessions = load_sessions()
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(14))

        header_row = BoxLayout(size_hint_y=None, height=dp(36))
        title = Label(
            text="Jurnal",
            color=(0.93, 0.93, 0.92, 1),
            font_size="22sp",
            bold=True,
            halign="left",
        )
        title.bind(size=title.setter("text_size"))
        back_btn = Builder.load_string("GhostButton:")
        back_btn.text = "< Orqaga"
        back_btn.size_hint_x = None
        back_btn.width = dp(110)
        back_btn.bind(on_press=lambda *a: setattr(self.manager, "current", "setup"))
        header_row.add_widget(title)
        header_row.add_widget(back_btn)
        root.add_widget(header_row)

        if not sessions:
            empty = Label(
                text="Hali sessiya yo'q.\n\"Boshlash\" bilan birinchi mashqni qiling.",
                color=(0.55, 0.55, 0.56, 1),
                font_size="14sp",
                halign="center",
            )
            root.add_widget(empty)
            self.add_widget(root)
            return

        best = max(s["correct"] for s in sessions)
        avg = round(sum(s["correct"] for s in sessions) / len(sessions))

        stats_row = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10))
        stats_row.add_widget(self._stat_card("ENG YAXSHI", str(best), (0.769, 0.945, 0.208, 1)))
        stats_row.add_widget(self._stat_card("O'RTACHA", str(avg), (0.29, 0.49, 0.49, 1)))
        stats_row.add_widget(self._stat_card("JAMI", str(len(sessions)), (0.93, 0.93, 0.92, 1)))
        root.add_widget(stats_row)

        scroll = ScrollView()
        session_list = GridLayout(cols=1, size_hint_y=None, spacing=dp(8))
        session_list.bind(minimum_height=session_list.setter("height"))

        for s in sessions:
            session_list.add_widget(self._session_row(s))

        scroll.add_widget(session_list)
        root.add_widget(scroll)

        self.add_widget(root)

    def _stat_card(self, label, value, color):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(4))
        with box.canvas.before:
            Color(0.09, 0.1, 0.11, 1)
            box._bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(6)])
        box.bind(
            pos=lambda inst, val: setattr(inst._bg, "pos", val),
            size=lambda inst, val: setattr(inst._bg, "size", val),
        )
        lbl1 = Label(text=label, color=(0.55, 0.55, 0.56, 1), font_size="10sp", bold=True, size_hint_y=None, height=dp(16))
        lbl2 = Label(text=value, color=color, font_size="22sp", bold=True)
        box.add_widget(lbl1)
        box.add_widget(lbl2)
        return box

    def _session_row(self, s):
        row = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(64), padding=[dp(12), dp(8)])
        with row.canvas.before:
            Color(0.09, 0.1, 0.11, 1)
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(6)])
        row.bind(
            pos=lambda inst, val: setattr(inst._bg, "pos", val),
            size=lambda inst, val: setattr(inst._bg, "size", val),
        )

        try:
            dt = datetime.fromisoformat(s["date"])
            date_str = dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            date_str = ""

        top = f"{s['correct']} to'g'ri"
        if s.get("errors", 0) > 0:
            
