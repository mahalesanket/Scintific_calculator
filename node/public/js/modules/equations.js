class EquationSolver {
  static solveQuadratic(a, b, c) {
    const disc = b * b - 4 * a * c;
    if (disc > 0) {
      const x1 = (-b + Math.sqrt(disc)) / (2 * a);
      const x2 = (-b - Math.sqrt(disc)) / (2 * a);
      return `x₁ = ${x1}, x₂ = ${x2}`;
    } else if (disc === 0) {
      return `x = ${-b / (2 * a)}`;
    } else {
      const re = (-b / (2 * a)).toFixed(4);
      const im = (Math.sqrt(-disc) / (2 * a)).toFixed(4);
      return `x₁ = ${re} + ${im}i, x₂ = ${re} - ${im}i`;
    }
  }

  static solveLinearSystem2x2(a1, b1, c1, a2, b2, c2) {
    const D = a1 * b2 - a2 * b1;
    if (D === 0) throw new Error('System has no unique solution (Determinant = 0)');
    const Dx = c1 * b2 - c2 * b1;
    const Dy = a1 * c2 - a2 * c1;
    return { x: Dx / D, y: Dy / D };
  }
}