/**
 * Interactive Function Plotter & Graphing Module
 * Renders mathematical functions to an HTML5 Canvas context.
 */
class GraphingModule {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) {
      console.warn(`Canvas element #${canvasId} not found.`);
      return;
    }
    this.ctx = this.canvas.getContext('2d');
    
    // Viewport bounds in graph coordinates
    this.xMin = -10;
    this.xMax = 10;
    this.yMin = -10;
    this.yMax = 10;

    this.initEvents();
  }

  /**
   * Converts Graph X coordinate to Canvas Pixel X
   */
  toPixelX(x) {
    return ((x - this.xMin) / (this.xMax - this.xMin)) * this.canvas.width;
  }

  /**
   * Converts Graph Y coordinate to Canvas Pixel Y
   */
  toPixelY(y) {
    return this.canvas.height - ((y - this.yMin) / (this.yMax - this.yMin)) * this.canvas.height;
  }

  /**
   * Clears the canvas and renders grid axes
   */
  drawGrid() {
    const { width, height } = this.canvas;
    this.ctx.clearRect(0, 0, width, height);

    this.ctx.strokeStyle = '#2d2d3a';
    this.ctx.lineWidth = 1;

    // Draw vertical grid lines
    const xStep = Math.pow(10, Math.floor(Math.log10(this.xMax - this.xMin))) / 2;
    const startX = Math.ceil(this.xMin / xStep) * xStep;
    
    for (let x = startX; x <= this.xMax; x += xStep) {
      const px = this.toPixelX(x);
      this.ctx.beginPath();
      this.ctx.moveTo(px, 0);
      this.ctx.lineTo(px, height);
      this.ctx.stroke();
    }

    // Draw horizontal grid lines
    const yStep = Math.pow(10, Math.floor(Math.log10(this.yMax - this.yMin))) / 2;
    const startY = Math.ceil(this.yMin / yStep) * yStep;

    for (let y = startY; y <= this.yMax; y += yStep) {
      const py = this.toPixelY(y);
      this.ctx.beginPath();
      this.ctx.moveTo(0, py);
      this.ctx.lineTo(width, py);
      this.ctx.stroke();
    }

    // Draw Main X and Y Axes
    this.ctx.strokeStyle = '#8a8a9e';
    this.ctx.lineWidth = 2;

    const zeroX = this.toPixelX(0);
    const zeroY = this.toPixelY(0);

    // X-Axis
    this.ctx.beginPath();
    this.ctx.moveTo(0, zeroY);
    this.ctx.lineTo(width, zeroY);
    this.ctx.stroke();

    // Y-Axis
    this.ctx.beginPath();
    this.ctx.moveTo(zeroX, 0);
    this.ctx.lineTo(zeroX, height);
    this.ctx.stroke();
  }

  /**
   * Evaluates and plots a function y = f(x)
   * @param {Function} func - JavaScript function taking x as a input number and returning y
   * @param {string} color - CSS stroke style for the curve
   */
  plotFunction(func, color = '#2b7fff') {
    this.drawGrid();

    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = 2.5;
    this.ctx.beginPath();

    const step = (this.xMax - this.xMin) / this.canvas.width;
    let isDrawing = false;

    for (let px = 0; px <= this.canvas.width; px++) {
      const x = this.xMin + px * step;
      try {
        const y = func(x);

        if (isNaN(y) || !isFinite(y) || y < this.yMin - 100 || y > this.yMax + 100) {
          isDrawing = false;
          continue;
        }

        const py = this.toPixelY(y);

        if (!isDrawing) {
          this.ctx.moveTo(px, py);
          isDrawing = true;
        } else {
          this.ctx.lineTo(px, py);
        }
      } catch (e) {
        isDrawing = false;
      }
    }

    this.ctx.stroke();
  }

  /**
   * Event listeners for Canvas interactive zoom via wheel
   */
  initEvents() {
    if (!this.canvas) return;

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 0.9 : 1.1;

      const xCenter = (this.xMin + this.xMax) / 2;
      const yCenter = (this.yMin + this.yMax) / 2;

      const xSpan = (this.xMax - this.xMin) * zoomFactor;
      const ySpan = (this.yMax - this.yMin) * zoomFactor;

      this.xMin = xCenter - xSpan / 2;
      this.xMax = xCenter + xSpan / 2;
      this.yMin = yCenter - ySpan / 2;
      this.yMax = yCenter + ySpan / 2;

      this.drawGrid();
    });
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = GraphingModule;
}