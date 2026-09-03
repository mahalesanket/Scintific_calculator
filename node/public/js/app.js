const engine = new CalculatorEngine();
let currentExpr = '';

const exprDisplay = document.getElementById('exprDisplay');
const resultDisplay = document.getElementById('resultDisplay');
const angleBtn = document.getElementById('btnAngle');
const memStatus = document.getElementById('memStatus');
const historyList = document.getElementById('historyList');

function updateDisplay() {
  exprDisplay.innerText = currentExpr;
}

function handleBtn(val) {
  if (val === 'AC') {
    currentExpr = '';
    resultDisplay.innerText = '0';
  } else if (val === 'CE') {
    currentExpr = currentExpr.slice(0, -1);
  } else if (val === 'MC') {
    engine.memoryClear();
    memStatus.innerText = 'M: 0';
  } else if (val === 'MR') {
    currentExpr += engine.memoryRecall();
  } else if (val === 'MS') {
    engine.memoryStore(resultDisplay.innerText);
    memStatus.innerText = `M: ${resultDisplay.innerText}`;
  } else if (val === 'M+') {
    engine.memoryAdd(resultDisplay.innerText);
    memStatus.innerText = `M: ${engine.memoryRecall()}`;
  } else if (val === 'M-') {
    engine.memorySub(resultDisplay.innerText);
    memStatus.innerText = `M: ${engine.memoryRecall()}`;
  } else {
    currentExpr += val;
  }
  updateDisplay();
}

function toggleAngleMode() {
  const modes = ['DEG', 'RAD', 'GRAD'];
  let nextIdx = (modes.indexOf(engine.angleMode) + 1) % modes.length;
  engine.setAngleMode(modes[nextIdx]);
  if (angleBtn) angleBtn.innerText = modes[nextIdx];
  const angleStatus = document.getElementById('angleStatus');
  if (angleStatus) angleStatus.innerText = modes[nextIdx];
}

function calculateResult() {
  try {
    if (!currentExpr.trim()) return;
    const result = engine.evaluate(currentExpr);
    resultDisplay.innerText = result;
    addHistory(currentExpr, result);
  } catch (err) {
    resultDisplay.innerText = err.message;
  }
}

function addHistory(expr, res) {
  if (!historyList) return;
  const item = document.createElement('div');
  item.className = 'history-item';
  item.innerHTML = `<div class="history-expr">${expr}</div><div class="history-res">= ${res}</div>`;
  historyList.prepend(item);
}

// Keyboard Integration
document.addEventListener('keydown', (e) => {
  if ((e.key >= '0' && e.key <= '9') || ['+', '-', '*', '/', '.', '(', ')', '^'].includes(e.key)) {
    handleBtn(e.key);
  } else if (e.key === 'Enter') {
    calculateResult();
  } else if (e.key === 'Backspace') {
    handleBtn('CE');
  } else if (e.key === 'Escape') {
    handleBtn('AC');
  }
});

// Theme switcher
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    document.documentElement.setAttribute('data-theme', currentTheme === 'dark' ? 'light' : 'dark');
  });
}