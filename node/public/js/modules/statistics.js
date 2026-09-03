class StatisticsModule {
  static analyze1Var(data) {
    if (!data || data.length === 0) throw new Error('No dataset provided');
    const n = data.length;
    const sum = data.reduce((a, b) => a + b, 0);
    const mean = sum / n;
    const sorted = [...data].sort((a, b) => a - b);
    const median = n % 2 === 0 ? (sorted[n / 2 - 1] + sorted[n / 2]) / 2 : sorted[Math.floor(n / 2)];
    const min = sorted[0];
    const max = sorted[n - 1];
    
    const variance = data.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / (n - 1 || 1);
    const stdDev = Math.sqrt(variance);

    return { n, mean, median, min, max, variance, stdDev, sum };
  }

  static linearRegression(x, y) {
    if (x.length !== y.length || x.length === 0) throw new Error('Invalid regression datasets');
    const n = x.length;
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((acc, val, i) => acc + val * y[i], 0);
    const sumX2 = x.reduce((acc, val) => acc + val * val, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    return { slope, intercept };
  }
}