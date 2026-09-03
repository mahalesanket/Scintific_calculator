const express = require('express');
const path = require('path');
const { create, all } = require('mathjs');
const Decimal = require('decimal.js');

const app = express();
const PORT = process.env.PORT || 3000;

const math = create(all, {
  number: 'BigNumber',
  precision: 64
});

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Health Check Endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Optional Calculation API (Safe evaluation without eval)
app.post('/api/evaluate', (req, res) => {
  const { expression, angleMode = 'DEG' } = req.body;

  if (!expression || typeof expression !== 'string') {
    return res.status(400).json({ error: 'Valid string expression is required.' });
  }

  try {
    // Transform trigonometric functions according to angle mode if necessary
    let parsedExpr = expression;
    if (angleMode === 'DEG') {
      parsedExpr = parsedExpr.replace(/sin\(([^)]+)\)/g, 'sin(($1) * deg)');
      parsedExpr = parsedExpr.replace(/cos\(([^)]+)\)/g, 'cos(($1) * deg)');
      parsedExpr = parsedExpr.replace(/tan\(([^)]+)\)/g, 'tan(($1) * deg)');
    } else if (angleMode === 'GRAD') {
      parsedExpr = parsedExpr.replace(/sin\(([^)]+)\)/g, 'sin(($1) * (pi / 200))');
      parsedExpr = parsedExpr.replace(/cos\(([^)]+)\)/g, 'cos(($1) * (pi / 200))');
      parsedExpr = parsedExpr.replace(/tan\(([^)]+)\)/g, 'tan(($1) * (pi / 200))');
    }

    const compiled = math.compile(parsedExpr);
    const result = compiled.evaluate();
    
    res.json({
      expression,
      result: math.format(result, { precision: 14 })
    });
  } catch (err) {
    res.status(400).json({ error: 'Math Error: Invalid expression' });
  }
});

app.listen(PORT, () => {
  console.log(`Calculator Server running on http://localhost:${PORT}`);
});