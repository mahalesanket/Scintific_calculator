/**
 * Scientific Unit Converter Module
 */
class UnitConverterModule {
  static conversionFactors = {
    length: {
      m: 1,
      km: 1000,
      cm: 0.01,
      mm: 0.001,
      mile: 1609.344,
      yard: 0.9144,
      foot: 0.3048,
      inch: 0.0254
    },
    mass: {
      kg: 1,
      g: 0.001,
      mg: 0.000001,
      lb: 0.45359237,
      oz: 0.028349523125,
      tonne: 1000
    },
    pressure: {
      pa: 1,
      kpa: 1000,
      bar: 100000,
      atm: 101325,
      psi: 6894.75729,
      torr: 133.322368
    },
    energy: {
      j: 1,
      kj: 1000,
      cal: 4.184,
      kcal: 4184,
      ev: 1.602176634e-19,
      kwh: 3600000,
      btu: 1055.05585
    },
    angle: {
      rad: 1,
      deg: Math.PI / 180,
      grad: Math.PI / 200,
      arcmin: Math.PI / (180 * 60),
      arcsec: Math.PI / (180 * 3600)
    }
  };

  /**
   * Converts generic proportional units
   */
  static convert(category, value, fromUnit, toUnit) {
    const cat = this.conversionFactors[category];
    if (!cat) throw new Error(`Unknown conversion category: ${category}`);
    if (!(fromUnit in cat) || !(toUnit in cat)) {
      throw new Error(`Unsupported unit in category ${category}`);
    }

    const baseValue = value * cat[fromUnit];
    return baseValue / cat[toUnit];
  }

  /**
   * Handles non-linear Temperature conversions separately
   */
  static convertTemperature(value, fromUnit, toUnit) {
    const from = fromUnit.toUpperCase();
    const to = toUnit.toUpperCase();

    if (from === to) return value;

    // Convert input to Kelvin as baseline
    let kelvin;
    switch (from) {
      case 'C': kelvin = value + 273.15; break;
      case 'F': kelvin = (value + 459.67) * (5 / 9); break;
      case 'K': kelvin = value; break;
      default: throw new Error(`Invalid source temperature unit: ${fromUnit}`);
    }

    // Convert Kelvin to target unit
    switch (to) {
      case 'C': return kelvin - 273.15;
      case 'F': return kelvin * (9 / 5) - 459.67;
      case 'K': return kelvin;
      default: throw new Error(`Invalid target temperature unit: ${toUnit}`);
    }
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = UnitConverterModule;
}