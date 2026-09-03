import sys
import math
import datetime
from decimal import Decimal, getcontext
import numpy as np
import scipy.stats as stats
import sympy as sp

from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem,
    QTabWidget, QSplitter, QGroupBox, QMessageBox, QFileDialog, QHeaderView
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# High precision setup
getcontext().prec = 30


# ==============================================================================
# 1. SAFE MATHEMATICAL EVALUATOR & AST PARSER
# ==============================================================================
class SafeEvaluator:
    """
    Safely parses and evaluates mathematical expressions using SymPy AST without eval().
    Handles angle unit conversions (DEG, RAD, GRAD) automatically.
    """

    def __init__(self):
        self.angle_mode = "DEG"  # DEG, RAD, GRAD

    def set_angle_mode(self, mode: str):
        if mode in ["DEG", "RAD", "GRAD"]:
            self.angle_mode = mode

    def _get_sympy_context(self):
        context = {
            'pi': sp.pi, 'e': sp.E, 'tau': 2 * sp.pi, 'phi': sp.GoldenRatio,
            'i': sp.I, 'I': sp.I, 'oo': sp.oo,
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
            'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
            'asinh': sp.asinh, 'acosh': sp.acosh, 'atanh': sp.atanh,
            'sqrt': sp.sqrt, 'cbrt': lambda x: x**(1/sp.S(3)),
            'log': lambda x, base=10: sp.log(x, base),
            'ln': sp.log, 'log2': lambda x: sp.log(x, 2),
            'exp': sp.exp, 'abs': sp.Abs, 'factorial': sp.factorial,
            'mod': sp.Mod, 'nPr': lambda n, r: sp.factorial(n) / sp.factorial(n - r),
            'nCr': lambda n, r: sp.binomial(n, r)
        }

        if self.angle_mode == "DEG":
            context['sin'] = lambda x: sp.sin(x * sp.pi / 180)
            context['cos'] = lambda x: sp.cos(x * sp.pi / 180)
            context['tan'] = lambda x: sp.tan(x * sp.pi / 180)
            context['asin'] = lambda x: sp.asin(x) * 180 / sp.pi
            context['acos'] = lambda x: sp.acos(x) * 180 / sp.pi
            context['atan'] = lambda x: sp.atan(x) * 180 / sp.pi
        elif self.angle_mode == "GRAD":
            context['sin'] = lambda x: sp.sin(x * sp.pi / 200)
            context['cos'] = lambda x: sp.cos(x * sp.pi / 200)
            context['tan'] = lambda x: sp.tan(x * sp.pi / 200)
            context['asin'] = lambda x: sp.asin(x) * 200 / sp.pi
            context['acos'] = lambda x: sp.acos(x) * 200 / sp.pi
            context['atan'] = lambda x: sp.atan(x) * 200 / sp.pi

        return context

    def evaluate(self, expr_str: str, ans_val=0, variables=None) -> tuple[bool, str, sp.Expr]:
        try:
            cleaned = (expr_str.replace('×', '*')
                       .replace('÷', '/')
                       .replace('−', '-')
                       .replace('π', 'pi')
                       .replace('√', 'sqrt')
                       .replace('ANS', str(ans_val)))

            local_dict = self._get_sympy_context()
            if variables:
                local_dict.update(variables)

            parsed_expr = sp.parse_expr(cleaned, local_dict=local_dict, transformations='all')
            eval_result = parsed_expr.evalf()
            
            if eval_result.is_number and not eval_result.is_complex:
                float_val = float(eval_result)
                if abs(float_val - round(float_val)) < 1e-12:
                    display_str = str(int(round(float_val)))
                else:
                    display_str = f"{float_val:.10g}"
            else:
                display_str = str(eval_result)

            return True, display_str, eval_result
        except Exception as e:
            return False, f"Error: {str(e)}", None


# ==============================================================================
# 2. STYLESHEETS
# ==============================================================================
DARK_THEME = """
QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox { background-color: #11111b; color: #a6e3a1; border: 1px solid #45475a; border-radius: 6px; padding: 6px; font-size: 15px; }
QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 8px; font-weight: bold; }
QPushButton:hover { background-color: #45475a; }
QPushButton:pressed { background-color: #585b70; }
QPushButton[btnClass="num"] { background-color: #181825; color: #89b4fa; font-size: 15px; }
QPushButton[btnClass="op"] { background-color: #fab387; color: #11111b; font-size: 15px; }
QPushButton[btnClass="fn"] { background-color: #313244; color: #f5e0dc; }
QPushButton[btnClass="action"] { background-color: #f38ba8; color: #11111b; }
QTableWidget, QTextEdit { background-color: #181825; color: #cdd6f4; border: 1px solid #45475a; gridline-color: #313244; }
QHeaderView::section { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; padding: 4px; }
QGroupBox { font-weight: bold; border: 1px solid #45475a; border-radius: 6px; margin-top: 6px; padding-top: 10px; }
"""

LIGHT_THEME = """
QWidget { background-color: #f8f9fa; color: #212529; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox { background-color: #ffffff; color: #0d6efd; border: 1px solid #ced4da; border-radius: 6px; padding: 6px; font-size: 15px; }
QPushButton { background-color: #e9ecef; color: #212529; border: 1px solid #ced4da; border-radius: 6px; padding: 8px; font-weight: bold; }
QPushButton:hover { background-color: #dee2e6; }
QPushButton:pressed { background-color: #ced4da; }
QPushButton[btnClass="num"] { background-color: #ffffff; color: #0d6efd; font-size: 15px; }
QPushButton[btnClass="op"] { background-color: #fd7e14; color: #ffffff; font-size: 15px; }
QPushButton[btnClass="fn"] { background-color: #e2e3e5; color: #495057; }
QPushButton[btnClass="action"] { background-color: #dc3545; color: #ffffff; }
QTableWidget, QTextEdit { background-color: #ffffff; color: #212529; border: 1px solid #ced4da; gridline-color: #e9ecef; }
QHeaderView::section { background-color: #e9ecef; color: #212529; border: 1px solid #ced4da; padding: 4px; }
QGroupBox { font-weight: bold; border: 1px solid #ced4da; border-radius: 6px; margin-top: 6px; padding-top: 10px; }
"""


# ==============================================================================
# 3. SCIENTIFIC MODE
# ==============================================================================
class ScientificModeWidget(QWidget):
    def __init__(self, core_evaluator, history_callback):
        super().__init__()
        self.evaluator = core_evaluator
        self.history_callback = history_callback
        self.memory = 0.0
        self.ans = 0.0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        status_layout = QHBoxLayout()
        self.lbl_angle = QLabel("ANGLE: DEG")
        self.lbl_angle.setStyleSheet("font-weight: bold; color: #f9e2af;")
        self.lbl_mem = QLabel("MEM: 0")
        self.lbl_mem.setStyleSheet("font-weight: bold; color: #a6e3a1;")
        status_layout.addWidget(self.lbl_angle)
        status_layout.addStretch()
        status_layout.addWidget(self.lbl_mem)
        layout.addLayout(status_layout)

        self.expr_display = QLineEdit()
        self.expr_display.setPlaceholderText("Enter expression...")
        self.result_display = QLineEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setAlignment(Qt.AlignRight)
        self.result_display.setPlaceholderText("0")
        
        layout.addWidget(self.expr_display)
        layout.addWidget(self.result_display)

        buttons = [
            [('MC', 'fn'), ('MR', 'fn'), ('MS', 'fn'), ('M+', 'fn'), ('M-', 'fn'), ('ANS', 'fn'), ('DEG/RAD', 'fn')],
            [('sin', 'fn'), ('cos', 'fn'), ('tan', 'fn'), ('log', 'fn'), ('ln', 'fn'), ('√', 'fn'), ('x²', 'fn'), ('xʸ', 'fn')],
            [('sinh', 'fn'), ('cosh', 'fn'), ('tanh', 'fn'), ('asin', 'fn'), ('acos', 'fn'), ('atan', 'fn'), ('π', 'fn'), ('e', 'fn')],
            [('7', 'num'), ('8', 'num'), ('9', 'num'), ('÷', 'op'), ('(', 'fn'), (')', 'fn'), ('DEL', 'action'), ('AC', 'action')],
            [('4', 'num'), ('5', 'num'), ('6', 'num'), ('×', 'op'), ('%', 'fn'), ('n!', 'fn'), ('1/x', 'fn'), ('+/-', 'fn')],
            [('1', 'num'), ('2', 'num'), ('3', 'num'), ('-', 'op'), ('mod', 'fn'), ('|x|', 'fn'), ('EXP', 'fn'), ('=', 'op')],
            [('0', 'num'), ('.', 'num'), ('+', 'op'), ('nPr', 'fn'), ('nCr', 'fn'), ('log2', 'fn'), ('∛', 'fn'), ('10ˣ', 'fn')]
        ]

        grid = QGridLayout()
        grid.setSpacing(6)
        for r, row in enumerate(buttons):
            for c, (text, cls) in enumerate(row):
                btn = QPushButton(text)
                btn.setProperty("btnClass", cls)
                btn.setMinimumSize(45, 40)
                btn.clicked.connect(lambda ch, t=text: self.on_button_click(t))
                grid.addWidget(btn, r, c)

        layout.addLayout(grid)

    def on_button_click(self, text: str):
        cursor_pos = self.expr_display.cursorPosition()
        current_text = self.expr_display.text()

        if text == 'AC':
            self.expr_display.clear()
            self.result_display.clear()
        elif text == 'DEL':
            if cursor_pos > 0:
                self.expr_display.setText(current_text[:cursor_pos-1] + current_text[cursor_pos:])
                self.expr_display.setCursorPosition(cursor_pos - 1)
        elif text == '=':
            self.calculate()
        elif text == 'DEG/RAD':
            new_mode = "RAD" if self.evaluator.angle_mode == "DEG" else "DEG"
            self.evaluator.set_angle_mode(new_mode)
            self.lbl_angle.setText(f"ANGLE: {new_mode}")
        elif text == 'MS':
            self.memory = self.get_current_result_val()
            self.lbl_mem.setText(f"MEM: {self.memory}")
        elif text == 'MC':
            self.memory = 0.0
            self.lbl_mem.setText("MEM: 0")
        elif text == 'MR':
            self.insert_text(str(self.memory))
        elif text == 'M+':
            self.memory += self.get_current_result_val()
            self.lbl_mem.setText(f"MEM: {self.memory}")
        elif text == 'M-':
            self.memory -= self.get_current_result_val()
            self.lbl_mem.setText(f"MEM: {self.memory}")
        elif text == 'x²': self.insert_text('^2')
        elif text == 'xʸ': self.insert_text('^')
        elif text == '1/x': self.insert_text('1/(')
        elif text == '10ˣ': self.insert_text('10^(')
        elif text == '∛': self.insert_text('cbrt(')
        elif text == '|x|': self.insert_text('abs(')
        elif text == 'n!': self.insert_text('factorial(')
        elif text in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'log', 'ln', 'log2', 'sqrt']:
            self.insert_text(f"{text}(")
        else:
            self.insert_text(text)

    def insert_text(self, text: str):
        pos = self.expr_display.cursorPosition()
        curr = self.expr_display.text()
        self.expr_display.setText(curr[:pos] + text + curr[pos:])
        self.expr_display.setCursorPosition(pos + len(text))

    def get_current_result_val(self) -> float:
        try:
            return float(self.result_display.text())
        except ValueError:
            return 0.0

    def calculate(self):
        expr = self.expr_display.text()
        if not expr.strip():
            return
        success, res_str, res_expr = self.evaluator.evaluate(expr, ans_val=self.ans)
        self.result_display.setText(res_str)
        if success and res_expr is not None:
            try:
                self.ans = float(res_expr)
            except Exception:
                pass
            self.history_callback(expr, res_str)


# ==============================================================================
# 4. EQUATION SOLVER MODE
# ==============================================================================
class EquationSolverWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Equation Solver (Single & Systems)</b>"))

        self.tab_eq = QTabWidget()

        # Tab 1: Single Polynomial/Algebraic Equation
        tab1 = QWidget()
        l1 = QVBoxLayout(tab1)
        l1.addWidget(QLabel("Enter equation in terms of <b>x</b> (e.g., <code>x^2 - 5*x + 6 = 0</code>):"))
        self.txt_single_eq = QLineEdit("x^2 - 5*x + 6 = 0")
        l1.addWidget(self.txt_single_eq)

        btn_solve_single = QPushButton("Solve for x")
        btn_solve_single.setProperty("btnClass", "op")
        btn_solve_single.clicked.connect(self.solve_single)
        l1.addWidget(btn_solve_single)
        l1.addStretch()
        self.tab_eq.addTab(tab1, "Single Equation")

        # Tab 2: System of Linear Equations
        tab2 = QWidget()
        l2 = QVBoxLayout(tab2)
        l2.addWidget(QLabel("Enter system of equations (comma-separated, variables: <b>x, y, z</b>):"))
        self.txt_sys_eq = QTextEdit("2*x + y = 10\nx - 2*y = 0")
        self.txt_sys_eq.setMaximumHeight(80)
        l2.addWidget(self.txt_sys_eq)

        btn_solve_sys = QPushButton("Solve System")
        btn_solve_sys.setProperty("btnClass", "op")
        btn_solve_sys.clicked.connect(self.solve_system)
        l2.addWidget(btn_solve_sys)
        l2.addStretch()
        self.tab_eq.addTab(tab2, "System of Equations")

        layout.addWidget(self.tab_eq)

        self.txt_out = QTextEdit()
        self.txt_out.setReadOnly(True)
        layout.addWidget(self.txt_out)

    def solve_single(self):
        try:
            eq_str = self.txt_single_eq.text().replace('^', '**')
            x = sp.Symbol('x')
            if '=' in eq_str:
                lhs_str, rhs_str = eq_str.split('=')
                lhs = sp.parse_expr(lhs_str)
                rhs = sp.parse_expr(rhs_str)
                eq = sp.Eq(lhs, rhs)
            else:
                eq = sp.Eq(sp.parse_expr(eq_str), 0)

            solutions = sp.solve(eq, x)
            output = f"<b>Solutions for x:</b><br>"
            for idx, sol in enumerate(solutions, 1):
                output += f"x<sub>{idx}</sub> = <b>{sp.pretty(sol)}</b> (approx: {sol.evalf():.6g})<br>"
            self.txt_out.setHtml(output)
        except Exception as e:
            self.txt_out.setText(f"Error solving equation: {str(e)}")

    def solve_system(self):
        try:
            raw_lines = self.txt_sys_eq.toPlainText().strip().split('\n')
            symbols = sp.symbols('x y z')
            eqs = []

            for line in raw_lines:
                line = line.replace('^', '**').strip()
                if not line:
                    continue
                if '=' in line:
                    lhs_str, rhs_str = line.split('=')
                    eqs.append(sp.Eq(sp.parse_expr(lhs_str), sp.parse_expr(rhs_str)))
                else:
                    eqs.append(sp.Eq(sp.parse_expr(line), 0))

            solution = sp.solve(eqs, symbols)
            output = f"<b>System Solutions:</b><br>"
            if isinstance(solution, dict):
                for k, v in solution.items():
                    output += f"{k} = <b>{v}</b> (approx: {v.evalf():.6g})<br>"
            elif isinstance(solution, list):
                for item in solution:
                    output += f"Solution set: <b>{item}</b><br>"
            else:
                output += str(solution)

            self.txt_out.setHtml(output)
        except Exception as e:
            self.txt_out.setText(f"Error solving system: {str(e)}")


# ==============================================================================
# 5. FINANCIAL TVM & LOAN EMI CALCULATOR
# ==============================================================================
class FinancialTVMWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Financial TVM & Loan EMI Engine</b>"))

        grid = QGridLayout()

        # Input Parameters
        grid.addWidget(QLabel("Principal ($PV):"), 0, 0)
        self.sp_pv = QDoubleSpinBox(); self.sp_pv.setMaximum(1e9); self.sp_pv.setValue(100000.0)
        grid.addWidget(self.sp_pv, 0, 1)

        grid.addWidget(QLabel("Annual Rate (%):"), 1, 0)
        self.sp_rate = QDoubleSpinBox(); self.sp_rate.setMaximum(100.0); self.sp_rate.setValue(7.5)
        grid.addWidget(self.sp_rate, 1, 1)

        grid.addWidget(QLabel("Tenure (Years):"), 2, 0)
        self.sp_years = QDoubleSpinBox(); self.sp_years.setMaximum(100.0); self.sp_years.setValue(15.0)
        grid.addWidget(self.sp_years, 2, 1)

        grid.addWidget(QLabel("Compounding / Payments per Year:"), 3, 0)
        self.combo_py = QComboBox()
        self.combo_py.addItems(["12 (Monthly)", "1 (Annually)", "2 (Semi-Annually)", "4 (Quarterly)"])
        grid.addWidget(self.combo_py, 3, 1)

        layout.addLayout(grid)

        btn_box = QHBoxLayout()
        btn_emi = QPushButton("Calculate Loan EMI")
        btn_emi.setProperty("btnClass", "op")
        btn_fv = QPushButton("Calculate Future Value (FV)")
        btn_box.addWidget(btn_emi)
        btn_box.addWidget(btn_fv)
        layout.addLayout(btn_box)

        self.txt_out = QTextEdit()
        self.txt_out.setReadOnly(True)
        layout.addWidget(self.txt_out)

        btn_emi.clicked.connect(self.calc_emi)
        btn_fv.clicked.connect(self.calc_fv)

    def get_py_val(self) -> int:
        txt = self.combo_py.currentText()
        return int(txt.split()[0])

    def calc_emi(self):
        p = self.sp_pv.value()
        r_annual = self.sp_rate.value() / 100.0
        n_years = self.sp_years.value()
        py = self.get_py_val()

        r_per_period = r_annual / py
        total_payments = n_years * py

        if r_per_period > 0:
            emi = p * (r_per_period * (1 + r_per_period)**total_payments) / (((1 + r_per_period)**total_payments) - 1)
        else:
            emi = p / total_payments

        total_pay = emi * total_payments
        total_interest = total_pay - p

        out = f"<b>Loan EMI Results:</b><br>"
        out += f"Periodic Payment (EMI): <b>${emi:,.2f}</b><br>"
        out += f"Total Payments ({total_payments:.0f} periods): <b>${total_pay:,.2f}</b><br>"
        out += f"Total Interest Payable: <span style='color:#f38ba8;'><b>${total_interest:,.2f}</b></span>"
        self.txt_out.setHtml(out)

    def calc_fv(self):
        pv = self.sp_pv.value()
        r_annual = self.sp_rate.value() / 100.0
        n_years = self.sp_years.value()
        py = self.get_py_val()

        r_per_period = r_annual / py
        total_periods = n_years * py

        fv = pv * ((1 + r_per_period)**total_periods)
        interest_gained = fv - pv

        out = f"<b>Future Value (Compound Interest) Results:</b><br>"
        out += f"Initial Investment (PV): <b>${pv:,.2f}</b><br>"
        out += f"Future Value (FV): <span style='color:#a6e3a1;'><b>${fv:,.2f}</b></span><br>"
        out += f"Interest Gained: <b>${interest_gained:,.2f}</b>"
        self.txt_out.setHtml(out)


# ==============================================================================
# 6. GRAPHING MODE
# ==============================================================================
class GraphingModeWidget(QWidget):
    def __init__(self, evaluator):
        super().__init__()
        self.evaluator = evaluator
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        controls = QWidget()
        ctrl_layout = QVBoxLayout(controls)

        ctrl_layout.addWidget(QLabel("<b>Functions y = f(x)</b>"))
        self.txt_fn1 = QLineEdit("x^2 - 4")
        self.txt_fn2 = QLineEdit("2*x + 1")
        self.txt_fn3 = QLineEdit("sin(x)")
        ctrl_layout.addWidget(QLabel("y1:"))
        ctrl_layout.addWidget(self.txt_fn1)
        ctrl_layout.addWidget(QLabel("y2:"))
        ctrl_layout.addWidget(self.txt_fn2)
        ctrl_layout.addWidget(QLabel("y3:"))
        ctrl_layout.addWidget(self.txt_fn3)

        ctrl_layout.addWidget(QLabel("<b>Plot Range</b>"))
        range_box = QHBoxLayout()
        self.spin_xmin = QDoubleSpinBox(); self.spin_xmin.setValue(-10.0)
        self.spin_xmax = QDoubleSpinBox(); self.spin_xmax.setValue(10.0)
        range_box.addWidget(QLabel("Min:")); range_box.addWidget(self.spin_xmin)
        range_box.addWidget(QLabel("Max:")); range_box.addWidget(self.spin_xmax)
        ctrl_layout.addLayout(range_box)

        btn_plot = QPushButton("Plot Functions")
        btn_plot.setProperty("btnClass", "op")
        btn_plot.clicked.connect(self.plot)
        ctrl_layout.addWidget(btn_plot)
        ctrl_layout.addStretch()

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#1e1e2e')
        self.canvas = FigureCanvas(self.fig)

        layout.addWidget(controls, stretch=1)
        layout.addWidget(self.canvas, stretch=3)

    def plot(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#11111b')
        ax.tick_params(colors='#cdd6f4')
        ax.xaxis.label.set_color('#cdd6f4')
        ax.yaxis.label.set_color('#cdd6f4')
        ax.grid(True, color='#313244')

        xmin = self.spin_xmin.value()
        xmax = self.spin_xmax.value()
        x_vals = np.linspace(xmin, xmax, 400)

        x_sym = sp.Symbol('x')
        for i, fn_input in enumerate([self.txt_fn1, self.txt_fn2, self.txt_fn3]):
            expr_str = fn_input.text().strip()
            if not expr_str:
                continue
            success, _, expr = self.evaluator.evaluate(expr_str, variables={'x': x_sym})
            if success and expr is not None:
                try:
                    f_lambdified = sp.lambdify(x_sym, expr, modules=['numpy', 'math'])
                    y_vals = f_lambdified(x_vals)
                    ax.plot(x_vals, y_vals, label=f"y{i+1} = {expr_str}")
                except Exception as e:
                    print(f"Plot Error in y{i+1}: {e}")

        ax.legend(facecolor='#313244', edgecolor='#45475a', labelcolor='#cdd6f4')
        self.canvas.draw()


# ==============================================================================
# 7. CALCULUS & SYMBOLIC MODE
# ==============================================================================
class CalculusModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<b>Symbolic Calculus & Algebra Solver</b>"))

        self.input_expr = QLineEdit("x^3 - 5*x^2 + 6*x")
        layout.addWidget(QLabel("Expression f(x):"))
        layout.addWidget(self.input_expr)

        btn_box = QHBoxLayout()
        btn_diff = QPushButton("Differentiate (d/dx)")
        btn_integ = QPushButton("Integrate (∫ dx)")
        btn_expand = QPushButton("Expand")
        btn_factor = QPushButton("Factor")

        btn_box.addWidget(btn_diff)
        btn_box.addWidget(btn_integ)
        btn_box.addWidget(btn_expand)
        btn_box.addWidget(btn_factor)
        layout.addLayout(btn_box)

        self.out_display = QTextEdit()
        self.out_display.setReadOnly(True)
        layout.addWidget(self.out_display)

        btn_diff.clicked.connect(lambda: self.process_symbolic('diff'))
        btn_integ.clicked.connect(lambda: self.process_symbolic('integrate'))
        btn_expand.clicked.connect(lambda: self.process_symbolic('expand'))
        btn_factor.clicked.connect(lambda: self.process_symbolic('factor'))

    def process_symbolic(self, operation: str):
        x = sp.Symbol('x')
        try:
            parsed = sp.parse_expr(self.input_expr.text().replace('^', '**'))
            if operation == 'diff':
                res = sp.diff(parsed, x)
                op_label = "Derivative"
            elif operation == 'integrate':
                res = sp.integrate(parsed, x)
                op_label = "Indefinite Integral (+ C)"
            elif operation == 'expand':
                res = sp.expand(parsed)
                op_label = "Expanded Form"
            elif operation == 'factor':
                res = sp.factor(parsed)
                op_label = "Factored Form"

            self.out_display.setText(f"<b>{op_label}:</b><br>{sp.pretty(res)}")
        except Exception as e:
            self.out_display.setText(f"Error: {str(e)}")


# ==============================================================================
# 8. MATRIX CALCULATOR MODE
# ==============================================================================
class MatrixModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Matrix Operations (3x3 Engine)</b>"))

        grid_layout = QHBoxLayout()
        
        group_a = QGroupBox("Matrix A")
        lay_a = QVBoxLayout(group_a)
        self.tbl_a = QTableWidget(3, 3)
        self.init_table(self.tbl_a)
        lay_a.addWidget(self.tbl_a)
        grid_layout.addWidget(group_a)

        group_b = QGroupBox("Matrix B")
        lay_b = QVBoxLayout(group_b)
        self.tbl_b = QTableWidget(3, 3)
        self.init_table(self.tbl_b)
        lay_b.addWidget(self.tbl_b)
        grid_layout.addWidget(group_b)

        layout.addLayout(grid_layout)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("A + B")
        btn_mul = QPushButton("A × B")
        btn_det = QPushButton("det(A)")
        btn_inv = QPushButton("A⁻¹")
        
        btn_layout.addWidget(btn_add); btn_layout.addWidget(btn_mul)
        btn_layout.addWidget(btn_det); btn_layout.addWidget(btn_inv)
        layout.addLayout(btn_layout)

        self.txt_result = QTextEdit()
        self.txt_result.setReadOnly(True)
        layout.addWidget(self.txt_result)

        btn_add.clicked.connect(self.add_matrices)
        btn_mul.clicked.connect(self.multiply_matrices)
        btn_det.clicked.connect(self.det_a)
        btn_inv.clicked.connect(self.inv_a)

    def init_table(self, table):
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r in range(3):
            for c in range(3):
                table.setItem(r, c, QTableWidgetItem("0"))

    def get_matrix(self, table) -> np.ndarray:
        data = np.zeros((3, 3))
        for r in range(3):
            for c in range(3):
                item = table.item(r, c)
                data[r, c] = float(item.text()) if item and item.text() else 0.0
        return data

    def add_matrices(self):
        res = self.get_matrix(self.tbl_a) + self.get_matrix(self.tbl_b)
        self.txt_result.setText(f"Result (A + B):\n{res}")

    def multiply_matrices(self):
        res = np.matmul(self.get_matrix(self.tbl_a), self.get_matrix(self.tbl_b))
        self.txt_result.setText(f"Result (A × B):\n{res}")

    def det_a(self):
        det = np.linalg.det(self.get_matrix(self.tbl_a))
        self.txt_result.setText(f"Determinant det(A): {det:.6f}")

    def inv_a(self):
        try:
            inv = np.linalg.inv(self.get_matrix(self.tbl_a))
            self.txt_result.setText(f"Inverse A⁻¹:\n{inv}")
        except np.linalg.LinAlgError:
            self.txt_result.setText("Error: Matrix A is singular (non-invertible).")


# ==============================================================================
# 9. STATISTICS & REGRESSION MODE
# ==============================================================================
class StatisticsModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Statistical Analysis & Linear Regression</b>"))

        layout.addWidget(QLabel("Data Points X (comma-separated):"))
        self.txt_x = QLineEdit("10, 20, 30, 40, 50")
        layout.addWidget(self.txt_x)

        layout.addWidget(QLabel("Data Points Y (optional, for linear regression):"))
        self.txt_y = QLineEdit("12, 24, 29, 42, 51")
        layout.addWidget(self.txt_y)

        btn_calc = QPushButton("Calculate Metrics")
        btn_calc.setProperty("btnClass", "op")
        btn_calc.clicked.connect(self.analyze)
        layout.addWidget(btn_calc)

        self.txt_out = QTextEdit()
        self.txt_out.setReadOnly(True)
        layout.addWidget(self.txt_out)

    def analyze(self):
        try:
            x_arr = np.array([float(v.strip()) for v in self.txt_x.text().split(',') if v.strip()])
            res_str = f"<b>1-Variable Statistics (X):</b><br>"
            res_str += f"Count (n): {len(x_arr)}<br>"
            res_str += f"Mean: {np.mean(x_arr):.4f}<br>"
            res_str += f"Median: {np.median(x_arr):.4f}<br>"
            res_str += f"Std Dev (Sample): {np.std(x_arr, ddof=1):.4f}<br>"
            res_str += f"Variance: {np.var(x_arr, ddof=1):.4f}<br>"
            res_str += f"Min / Max: {np.min(x_arr)} / {np.max(x_arr)}<br><br>"

            if self.txt_y.text().strip():
                y_arr = np.array([float(v.strip()) for v in self.txt_y.text().split(',') if v.strip()])
                if len(x_arr) == len(y_arr):
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_arr, y_arr)
                    res_str += f"<b>Linear Regression (y = mx + c):</b><br>"
                    res_str += f"Slope (m): {slope:.4f}<br>"
                    res_str += f"Intercept (c): {intercept:.4f}<br>"
                    res_str += f"Correlation R²: {r_value**2:.4f}<br>"

            self.txt_out.setHtml(res_str)
        except Exception as e:
            self.txt_out.setText(f"Error parsing data: {str(e)}")


# ==============================================================================
# 10. PROGRAMMER / BASE-N MODE
# ==============================================================================
class ProgrammerModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Base-N Conversion & Bitwise Logic</b>"))

        self.txt_val = QLineEdit("255")
        layout.addWidget(QLabel("Input Decimal Integer:"))
        layout.addWidget(self.txt_val)

        grid = QGridLayout()
        grid.addWidget(QLabel("HEX:"), 0, 0); self.lbl_hex = QLineEdit(); grid.addWidget(self.lbl_hex, 0, 1)
        grid.addWidget(QLabel("DEC:"), 1, 0); self.lbl_dec = QLineEdit(); grid.addWidget(self.lbl_dec, 1, 1)
        grid.addWidget(QLabel("OCT:"), 2, 0); self.lbl_oct = QLineEdit(); grid.addWidget(self.lbl_oct, 2, 1)
        grid.addWidget(QLabel("BIN:"), 3, 0); self.lbl_bin = QLineEdit(); grid.addWidget(self.lbl_bin, 3, 1)
        layout.addLayout(grid)

        self.txt_val.textChanged.connect(self.update_bases)
        self.update_bases()

    def update_bases(self):
        try:
            val = int(self.txt_val.text().strip())
            self.lbl_hex.setText(hex(val).upper().replace('0X', ''))
            self.lbl_dec.setText(str(val))
            self.lbl_oct.setText(oct(val).replace('0o', ''))
            self.lbl_bin.setText(bin(val).replace('0b', ''))
        except ValueError:
            for l in [self.lbl_hex, self.lbl_dec, self.lbl_oct, self.lbl_bin]:
                l.setText("Invalid Input")


# ==============================================================================
# 11. UNIT & CONVERSION ENGINE
# ==============================================================================
class UnitConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.units = {
            "Length": {"Meter": 1.0, "Kilometer": 1000.0, "Centimeter": 0.01, "Mile": 1609.34, "Foot": 0.3048},
            "Weight": {"Kilogram": 1.0, "Gram": 0.001, "Pound": 0.453592, "Ounce": 0.0283495},
            "Speed": {"m/s": 1.0, "km/h": 0.277778, "mph": 0.44704, "Knot": 0.514444}
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Multi-Category Unit Converter</b>"))

        self.combo_cat = QComboBox()
        self.combo_cat.addItems(list(self.units.keys()))
        layout.addWidget(self.combo_cat)

        conv_box = QHBoxLayout()
        self.val_from = QDoubleSpinBox(); self.val_from.setValue(1.0); self.val_from.setMaximum(1e9)
        self.combo_from = QComboBox()
        self.combo_to = QComboBox()
        self.val_to = QLineEdit(); self.val_to.setReadOnly(True)

        conv_box.addWidget(self.val_from)
        conv_box.addWidget(self.combo_from)
        conv_box.addWidget(QLabel("➔"))
        conv_box.addWidget(self.val_to)
        conv_box.addWidget(self.combo_to)
        layout.addLayout(conv_box)

        self.combo_cat.currentTextChanged.connect(self.populate_units)
        self.val_from.valueChanged.connect(self.convert)
        self.combo_from.currentTextChanged.connect(self.convert)
        self.combo_to.currentTextChanged.connect(self.convert)

        self.populate_units()

    def populate_units(self):
        cat = self.combo_cat.currentText()
        self.combo_from.clear()
        self.combo_to.clear()
        self.combo_from.addItems(list(self.units[cat].keys()))
        self.combo_to.addItems(list(self.units[cat].keys()))
        self.convert()

    def convert(self):
        cat = self.combo_cat.currentText()
        u_from = self.combo_from.currentText()
        u_to = self.combo_to.currentText()

        if u_from in self.units[cat] and u_to in self.units[cat]:
            base_val = self.val_from.value() * self.units[cat][u_from]
            res = base_val / self.units[cat][u_to]
            self.val_to.setText(f"{res:.6g}")


# ==============================================================================
# 12. MAIN WINDOW APPLICATION FRAMEWORK
# ==============================================================================
class AdvancedScientificCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Scientific Calculator Suite")
        self.resize(1050, 720)
        self.evaluator = SafeEvaluator()
        self.is_dark_theme = True

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("<b>MODE:</b>"))
        
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "COMP / Scientific Mode",
            "Equation Solver",
            "Financial TVM & Loan EMI",
            "Graphing Mode",
            "Calculus & Symbolic",
            "Matrix Calculator",
            "Statistics & Regression",
            "Programmer / Base-N",
            "Unit Converter"
        ])
        top_bar.addWidget(self.mode_selector)

        top_bar.addStretch()

        btn_theme = QPushButton("Toggle Theme")
        btn_theme.clicked.connect(self.toggle_theme)
        top_bar.addWidget(btn_theme)

        main_layout.addLayout(top_bar)

        splitter = QSplitter(Qt.Horizontal)

        self.mode_stack = QStackedWidget()
        
        # Instantiate All Modules
        self.sci_mode = ScientificModeWidget(self.evaluator, self.add_history)
        self.eq_mode = EquationSolverWidget()
        self.tvm_mode = FinancialTVMWidget()
        self.graph_mode = GraphingModeWidget(self.evaluator)
        self.calc_mode = CalculusModeWidget()
        self.matrix_mode = MatrixModeWidget()
        self.stats_mode = StatisticsModeWidget()
        self.prog_mode = ProgrammerModeWidget()
        self.unit_mode = UnitConverterWidget()

        self.mode_stack.addWidget(self.sci_mode)
        self.mode_stack.addWidget(self.eq_mode)
        self.mode_stack.addWidget(self.tvm_mode)
        self.mode_stack.addWidget(self.graph_mode)
        self.mode_stack.addWidget(self.calc_mode)
        self.mode_stack.addWidget(self.matrix_mode)
        self.mode_stack.addWidget(self.stats_mode)
        self.mode_stack.addWidget(self.prog_mode)
        self.mode_stack.addWidget(self.unit_mode)

        splitter.addWidget(self.mode_stack)

        history_panel = QWidget()
        hist_layout = QVBoxLayout(history_panel)
        hist_layout.addWidget(QLabel("<b>Calculation History</b>"))
        
        self.hist_list = QTextEdit()
        self.hist_list.setReadOnly(True)
        hist_layout.addWidget(self.hist_list)

        btn_clear_hist = QPushButton("Clear History")
        btn_clear_hist.clicked.connect(lambda: self.hist_list.clear())
        hist_layout.addWidget(btn_clear_hist)

        splitter.addWidget(history_panel)
        splitter.setSizes([780, 270])

        main_layout.addWidget(splitter)

        self.mode_selector.currentIndexChanged.connect(self.mode_stack.setCurrentIndex)

    def add_history(self, expr: str, result: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"<span style='color:#89b4fa;'>[{timestamp}]</span> <b>{expr}</b> = <span style='color:#a6e3a1;'>{result}</span><br>"
        self.hist_list.append(entry)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def apply_theme(self):
        style = DARK_THEME if self.is_dark_theme else LIGHT_THEME
        self.setStyleSheet(style)


# ==============================================================================
# 13. APPLICATION ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedScientificCalculator()
    window.show()
    sys.exit(app.exec())