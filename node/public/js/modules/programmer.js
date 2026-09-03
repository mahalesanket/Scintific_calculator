class ProgrammerModule {
  static convert(val, fromBase) {
    const intVal = parseInt(val, fromBase);
    if (isNaN(intVal)) throw new Error('Invalid Base Input');
    return {
      BIN: intVal.toString(2).toUpperCase(),
      OCT: intVal.toString(8).toUpperCase(),
      DEC: intVal.toString(10),
      HEX: intVal.toString(16).toUpperCase()
    };
  }

  static bitwise(op, a, b) {
    switch (op) {
      case 'AND': return a & b;
      case 'OR': return a | b;
      case 'XOR': return a ^ b;
      case 'NOT': return ~a;
      case 'SHL': return a << b;
      case 'SHR': return a >> b;
      default: return 0;
    }
  }
}