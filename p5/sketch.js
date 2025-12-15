const MIN = 0;
const POS = 1;
const MAX = 2;

const sketchFunction = (p, offsetY = 0) => {
  // sketch code
  let increments = 30;

  // state
  let TOP = [-8, 0, 8];
  let MID = [-5, 1, 5];
  let BTM = [-2, 0, 2];

  let tickButton;
  let autoplayButton;
  let speedSlider;
  let autoplayEnabled = false;
  let autoplayInterval = null;

  // State input fields
  let topMinInput, topPosInput, topMaxInput;
  let midMinInput, midPosInput, midMaxInput;
  let btmMinInput, btmPosInput, btmMaxInput;

  p.setup = function() {
    p.createCanvas(600, 400);

    // Create tick button at the bottom
    tickButton = p.createButton('tick');
    tickButton.position(p.width / 2 - 60, offsetY + p.height + 10);
    tickButton.mousePressed(tick);

    // Create autoplay button
    autoplayButton = p.createButton('autoplay');
    autoplayButton.position(p.width / 2 + 10, offsetY + p.height + 10);
    autoplayButton.mousePressed(toggleAutoplay);

    // Create speed slider (100ms to 2000ms)
    speedSlider = p.createSlider(100, 2000, 500, 50);
    speedSlider.position(p.width / 2 - 100, offsetY + p.height + 50);
    speedSlider.style('width', '200px');
    speedSlider.input(updateSpeed);

    // Create state input fields
    let startX = p.width + 20;
    let startY = offsetY + 50;
    let spacing = 30;

    // TOP inputs
    p.createP('TOP:').position(startX, startY - 20).style('margin', '0');
    topMinInput = p.createInput(TOP[MIN].toString()).position(startX, startY).size(40);
    topPosInput = p.createInput(TOP[POS].toString()).position(startX + 50, startY).size(40);
    topMaxInput = p.createInput(TOP[MAX].toString()).position(startX + 100, startY).size(40);
    topMinInput.input(() => updateState(TOP, MIN, topMinInput));
    topPosInput.input(() => updateState(TOP, POS, topPosInput));
    topMaxInput.input(() => updateState(TOP, MAX, topMaxInput));

    // MID inputs
    p.createP('MID:').position(startX, startY + spacing * 2 - 20).style('margin', '0');
    midMinInput = p.createInput(MID[MIN].toString()).position(startX, startY + spacing * 2).size(40);
    midPosInput = p.createInput(MID[POS].toString()).position(startX + 50, startY + spacing * 2).size(40);
    midMaxInput = p.createInput(MID[MAX].toString()).position(startX + 100, startY + spacing * 2).size(40);
    midMinInput.input(() => updateState(MID, MIN, midMinInput));
    midPosInput.input(() => updateState(MID, POS, midPosInput));
    midMaxInput.input(() => updateState(MID, MAX, midMaxInput));

    // BTM inputs
    p.createP('BTM:').position(startX, startY + spacing * 4 - 20).style('margin', '0');
    btmMinInput = p.createInput(BTM[MIN].toString()).position(startX, startY + spacing * 4).size(40);
    btmPosInput = p.createInput(BTM[POS].toString()).position(startX + 50, startY + spacing * 4).size(40);
    btmMaxInput = p.createInput(BTM[MAX].toString()).position(startX + 100, startY + spacing * 4).size(40);
    btmMinInput.input(() => updateState(BTM, MIN, btmMinInput));
    btmPosInput.input(() => updateState(BTM, POS, btmPosInput));
    btmMaxInput.input(() => updateState(BTM, MAX, btmMaxInput));

    // Labels for MIN, POS, MAX
    p.createP('MIN').position(startX, startY - 40).size(40).style('margin', '0').style('font-size', '10px');
    p.createP('POS').position(startX + 50, startY - 40).size(40).style('margin', '0').style('font-size', '10px');
    p.createP('MAX').position(startX + 100, startY - 40).size(40).style('margin', '0').style('font-size', '10px');
  }

  p.draw = function() {
    // p.background(255);
    // p.clear();
    // p.background('rgba(255,255,255, 0.1)');

    // Draw three horizontal lines with colored squares
    drawLineWithSquare(TOP, 100, p.color(255, 0, 0));    // Red
    drawLineWithSquare(MID, 200, p.color(0, 255, 0));    // Green
    drawLineWithSquare(BTM, 300, p.color(0, 0, 255));    // Blue

    // Display speed slider value
    p.fill(0);
    p.noStroke();
    p.textAlign(p.CENTER);
    p.text(speedSlider.value() + 'ms', p.width / 2, offsetY + p.height + 85);
  }

  function drawLineWithSquare(state, y, squareColor) {
    // Draw horizontal line
    p.stroke(0);
    p.strokeWeight(1);
    p.line(50, y, p.width - 50, y);

    // Draw colored square in the center
    let centerX = p.width / 2;
    let squareSize = 20;

    let square_pos = centerX + state[POS] * increments
    let square_min = centerX + state[MIN] * increments
    let square_max = centerX + state[MAX] * increments

    // center
    p.stroke(p.color(0,0,0));
    p.fill(p.color(255,255,255));
    p.rectMode(p.CENTER);
    p.square(centerX, y, squareSize+4);

    // MIN
    p.stroke(p.color(0,0,0));
    p.fill(p.color(255,255,255));
    p.rectMode(p.CENTER);
    p.square(square_min, y, squareSize+4);
    p.square(square_max, y, squareSize+4);

    // square
    p.noStroke();
    p.fill(squareColor);
    p.rectMode(p.CENTER);
    p.square(square_pos, y, squareSize);
  }

  function tick() {
    p.background('rgba(255,255,255, 0.4)');

    // Handle TOP
    if (MID[POS] > 0) {
      TOP[POS] = TOP[POS] + 1
    } else if (MID[POS] < 0) {
      TOP[POS] = TOP[POS] - 1
    }
    // if (TOP[POS] > TOP[MAX]) TOP[POS] = TOP[MAX]
    // if (TOP[POS] < TOP[MIN]) TOP[POS] = TOP[MIN]

    // Handle Mid
    if (BTM[POS] > 0) {
      MID[POS] = MID[POS] + 1
    } else if (BTM[POS] < 0) {
      MID[POS] = MID[POS] - 1
    }
    if (MID[POS] > MID[MAX]) MID[POS] = MID[MAX]
    if (MID[POS] < MID[MIN]) MID[POS] = MID[MIN]

    // Handle BTM
    if (TOP[POS] > 0) {
      BTM[POS] = BTM[POS] - 1
    } else if (TOP[POS] < 0) {
      BTM[POS] = BTM[POS] + 1
    }
    if (BTM[POS] > BTM[MAX]) BTM[POS] = BTM[MAX]
    if (BTM[POS] < BTM[MIN]) BTM[POS] = BTM[MIN]
  }

  function toggleAutoplay() {
    autoplayEnabled = !autoplayEnabled;

    if (autoplayEnabled) {
      autoplayButton.html('stop');
      autoplayInterval = setInterval(tick, speedSlider.value());
    } else {
      autoplayButton.html('autoplay');
      if (autoplayInterval) {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
      }
    }
  }

  function updateSpeed() {
    // If autoplay is running, restart it with the new speed
    if (autoplayEnabled && autoplayInterval) {
      clearInterval(autoplayInterval);
      autoplayInterval = setInterval(tick, speedSlider.value());
    }
  }

  function updateState(stateArray, index, inputField) {
    let value = parseInt(inputField.value());
    if (!isNaN(value)) {
      stateArray[index] = value;
    }
  }
};

// Create two instances of the sketch
new p5(p => sketchFunction(p, 0), 'sketch1');
new p5(p => sketchFunction(p, 600), 'sketch2');
