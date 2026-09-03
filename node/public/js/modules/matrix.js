class MatrixModule {
  static add(A, B) {
    return A.map((row, i) => row.map((val, j) => val + B[i][j]));
  }

  static multiply(A, B) {
    const rowsA = A.length, colsA = A[0].length, colsB = B[0].length;
    let result = Array.from({ length: rowsA }, () => Array(colsB).fill(0));
    for (let i = 0; i < rowsA; i++) {
      for (let j = 0; j < colsB; j++) {
        for (let k = 0; k < colsA; k++) {
          result[i][j] += A[i][k] * B[k][j];
        }
      }
    }
    return result;
  }

  static determinant(M) {
    if (M.length === 2) return M[0][0] * M[1][1] - M[0][1] * M[1][0];
    if (M.length === 3) {
      return (
        M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) -
        M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0]) +
        M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0])
      );
    }
    throw new Error('Only 2x2 and 3x3 matrices supported directly');
  }
}