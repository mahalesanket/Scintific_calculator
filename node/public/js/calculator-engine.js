/**
 * Safe Mathematical Expression Parser and Calculator Engine
 * Handles arbitrary precision, AST compilation, and domain restrictions.
 */
class CalculatorEngine {
  constructor() {
    Decimal.set({ precision: 32, rounding: Decimal.ROUND_HALF_UP });
    this.angleMode = 'DEG'; // DEG, RAD, GRAD
    this.memory = new Decimal(0);
    this.ans = '0';
    this.precision = 10;
    this.notation = 'AUTO'; // AUTO, FIX, SCI, ENG
  }

  setAngleMode(mode) {
    if (['DEG', 'RAD', 'GRAD'].includes(mode)) {
      this.angleMode = mode;
    }
  }

  setPrecision(prec) {
    this.precision = parseInt(prec, 10) || 10;
  }

  setNotation(notat) {
    this.notation = notat;
  }

  // Safe expression evaluation using mathjs AST
  evaluate(expression) {
    try {
      if (!expression || expression.trim() === '') return '0';

      // 1. Standardize operators & replace shorthand symbols
      let cleaned = expression
        .replace(/×/g, '*')
        .replace(/÷/g, '/')
        .replace(/−/g, '-')
        .replace(/π/g, 'pi')
        .replace(/Ans/g, this.ans)
        .replace(/mod/g, '%');

      // 2. Define custom scope variables and constants explicitly
      let scope = {
        e: math.e,
        pi: math.pi,
        phi: 1.618033988749895,
        i: math.i,
        deg: Math.PI / 180,        // Converts Degrees to Radians
        grad: Math.PI / 200,       // Converts Gradians to Radians
        rad: 1                      // Radians baseline
      };

      // 3. Handle trigonometric transformations according to selected Angle Mode
      if (this.angleMode === 'DEG') {
        cleaned = cleaned.replace(/\bsin\(/g, 'sin(deg * ');
        cleaned = cleaned.replace(/\bcos\(/g, 'cos(deg * ');
        cleaned = cleaned.replace(/\btan\(/g, 'tan(deg * ');
      } else if (this.angleMode === 'GRAD') {
        cleaned = cleaned.replace(/\bsin\(/g, 'sin(grad * ');
        cleaned = cleaned.replace(/\bcos\(/g, 'cos(grad * ');
        cleaned = cleaned.replace(/\btan\(/g, 'tan(grad * ');
      }

      // 4. Safe compile and evaluate via Math.js AST parser
      const node = math.parse(cleaned);
      const code = node.compile();
      let res = code.evaluate(scope);

      // Convert inverse trig function outputs back to active angle mode
      if (typeof res === 'number') {
        if (this.angleMode === 'DEG' && (cleaned.includes('asin') || cleaned.includes('acos') || cleaned.includes('atan'))) {
          res = (res * 180) / Math.PI;
        } else if (this.angleMode === 'GRAD' && (cleaned.includes('asin') || cleaned.includes('acos') || cleaned.includes('atan'))) {
          res = (res * 200) / Math.PI;
        }
      }

      let formatted = this.formatResult(res);
      this.ans = formatted;
      return formatted;
    } catch (err) {
      if (err.message && err.message.includes('Undefined symbol')) {
        throw new Error('Syntax Error: Unknown symbol or variable');
      }
      throw new Error('Syntax Error: Invalid expression');
    }
  }

  formatResult(val) {
    if (val === undefined || val === null) return '0';

    // Handle Complex Numbers
    if (typeof val === 'object' && val.isComplex) {
      const re = this.formatResult(val.re);
      const im = this.formatResult(Math.abs(val.im));
      const sign = val.im >= 0 ? '+' : '-';
      return `${re} ${sign} ${im}i`;
    }

    let num = new Decimal(val.toString());
    if (num.isNaN()) throw new Error('Math Error: Result is Undefined');
    if (!num.isFinite()) throw new Error('Math Error: Division by Zero / Overflow');

    if (this.notation === 'FIX') {
      return num.toFixed(this.precision);
    } else if (this.notation === 'SCI') {
      return num.toExponential(this.precision);
    } else if (this.notation === 'ENG') {
      const exp = num.e - (num.e % 3);
      const mantissa = num.div(Decimal.pow(10, exp));
      return `${mantissa.toFixed(4)} e${exp >= 0 ? '+' : ''}${exp}`;
    }

    // Default AUTO formatting (prevents floating-point precision artifacts like 0.30000000000000004)
    let str = num.precision(this.precision).toString();
    if (str.includes('.') && !str.includes('e')) {
      str = str.replace(/\.?0+$/, '');
    }
    return str;
  }

  // Memory Operations
  memoryClear() { this.memory = new Decimal(0); }
  memoryRecall() { return this.memory.toString(); }
  memoryStore(val) { this.memory = new Decimal(val || 0); }
  memoryAdd(val) { this.memory = this.memory.add(new Decimal(val || 0)); }
  memorySub(val) { this.memory = this.memory.sub(new Decimal(val || 0)); }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = CalculatorEngine;
}