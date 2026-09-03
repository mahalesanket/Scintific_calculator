/**
 * Complex Number Module
 * Supports Rectangular (a + bi) and Polar (r ∠ θ) representations.
 */
class ComplexModule {
  /**
   * Adds two complex numbers (a + bi) + (c + di)
   */
  static add(z1, z2) {
    return {
      re: z1.re + z2.re,
      im: z1.im + z2.im
    };
  }

  /**
   * Subtracts z2 from z1: (a + bi) - (c + di)
   */
  static subtract(z1, z2) {
    return {
      re: z1.re - z2.re,
      im: z1.im - z2.im
    };
  }

  /**
   * Multiplies two complex numbers: (a + bi)(c + di) = (ac - bd) + (ad + bc)i
   */
  static multiply(z1, z2) {
    return {
      re: z1.re * z2.re - z1.im * z2.im,
      im: z1.re * z2.im + z1.im * z2.re
    };
  }

  /**
   * Divides z1 by z2: (z1 * z2*) / |z2|²
   */
  static divide(z1, z2) {
    const denom = z2.re * z2.re + z2.im * z2.im;
    if (denom === 0) throw new Error('Complex Math Error: Division by Zero');
    return {
      re: (z1.re * z2.re + z1.im * z2.im) / denom,
      im: (z1.im * z2.re - z1.re * z2.im) / denom
    };
  }

  /**
   * Calculates magnitude (r)
   */
  static abs(z) {
    return Math.hypot(z.re, z.im);
  }

  /**
   * Calculates phase angle (θ) in radians or degrees
   */
  static arg(z, useDegrees = false) {
    const rad = Math.atan2(z.im, z.re);
    return useDegrees ? (rad * 180) / Math.PI : rad;
  }

  /**
   * Converts Rectangular (re, im) to Polar Form { r, theta }
   */
  static toPolar(z, useDegrees = true) {
    return {
      r: this.abs(z),
      theta: this.arg(z, useDegrees)
    };
  }

  /**
   * Converts Polar Form (r, theta) to Rectangular { re, im }
   */
  static fromPolar(r, theta, isDegrees = true) {
    const rad = isDegrees ? (theta * Math.PI) / 180 : theta;
    return {
      re: r * Math.cos(rad),
      im: r * Math.sin(rad)
    };
  }

  /**
   * Formats a complex number as a readable string
   */
  static toString(z, precision = 4) {
    const reStr = z.re.toFixed(precision).replace(/\.?0+$/, '');
    const absIm = Math.abs(z.im).toFixed(precision).replace(/\.?0+$/, '');
    const sign = z.im >= 0 ? '+' : '-';
    
    if (z.im === 0) return reStr;
    if (z.re === 0) return `${z.im < 0 ? '-' : ''}${absIm}i`;
    return `${reStr} ${sign} ${absIm}i`;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = ComplexModule;
}