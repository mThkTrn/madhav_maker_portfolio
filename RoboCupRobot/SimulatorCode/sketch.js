// RoboCup Junior Soccer Simulator with Kicking, Turning, and Reset on Score

let robots = [];
let ball;
let field;
let scoreRed = 0;
let scoreBlue = 0;

// Speed parameters for each team:
let redSpeed = 2;
let blueSpeed = 1;

function setup() {
  createCanvas(800, 600);
  field = new Field(width, height);
  ball = new Ball(width / 2, height / 2);

  // Create one attacker and one defender per team.
  robots.push(new Robot(200, height / 2 - 50, "red", "attacker", attackingAlgorithm));
  robots.push(new Robot(200, height / 2 + 50, "red", "defender", defenderAlgorithm));
  robots.push(new Robot(width - 200, height / 2 - 50, "blue", "attacker", attackingAlgorithm));
  robots.push(new Robot(width - 200, height / 2 + 50, "blue", "defender", defenderAlgorithm));
}

function draw() {
  background(50, 200, 50);
  field.display();
  displayScore();

  ball.update();

  // Update all robots.
  for (let robot of robots) {
    robot.update();
  }
  
  // Check for scoring.
  let goalScored = false;
  for (let robot of robots) {
    if (ball.attachedTo === robot) {
      let dp = robot.getDribblerPos();
      // For Red team, if the dribbler enters the right goal area.
      if (
        robot.team === "red" &&
        dp.x >= width &&
        dp.y >= (height - field.goalHeight) / 2 &&
        dp.y <= (height + field.goalHeight) / 2
      ) {
        scoreRed++;
        resetAll();
        goalScored = true;
        break;
      }
      // For Blue team, if the dribbler enters the left goal area.
      if (
        robot.team === "blue" &&
        dp.x <= 0 &&
        dp.y >= (height - field.goalHeight) / 2 &&
        dp.y <= (height + field.goalHeight) / 2
      ) {
        scoreBlue++;
        resetAll();
        goalScored = true;
        break;
      }
    }
  }

  // Prevent robots from overlapping.
  resolveRobotCollisions();

  // Display all robots and the ball.
  for (let robot of robots) {
    robot.display();
  }
  ball.display();
}

function displayScore() {
  fill(255);
  textSize(24);
  textAlign(CENTER, TOP);
  text("Red: " + scoreRed + "   Blue: " + scoreBlue, width / 2, 10);
}

// Reset the ball and all robots to their starting positions.
function resetAll() {
  ball.reset();
  for (let robot of robots) {
    robot.resetPosition();
  }
}

// Prevent robots from overlapping by nudging them apart.
function resolveRobotCollisions() {
  for (let i = 0; i < robots.length; i++) {
    for (let j = i + 1; j < robots.length; j++) {
      let r1 = robots[i];
      let r2 = robots[j];
      let d = p5.Vector.dist(r1.pos, r2.pos);
      let minDist = r1.radius + r2.radius;
      if (d < minDist && d > 0) {
        let overlap = minDist - d;
        let collisionNormal = p5.Vector.sub(r2.pos, r1.pos).normalize();
        r1.pos.add(p5.Vector.mult(collisionNormal, -overlap / 2));
        r2.pos.add(p5.Vector.mult(collisionNormal, overlap / 2));
      }
    }
  }
}

//---------------------------------------------------------
// Field Class: Draws the field boundaries and goals
//---------------------------------------------------------
class Field {
  constructor(w, h) {
    this.w = w;
    this.h = h;
    // The goal "mouth" is drawn as a rectangle extending from the field.
    this.goalWidth = 20;
    this.goalHeight = 200;
  }
  
  display() {
    // Draw field boundaries and center line.
    stroke(255);
    noFill();
    rect(0, 0, this.w, this.h);
    line(this.w / 2, 0, this.w / 2, this.h);
    
    // Draw goal areas (semi-transparent yellow) outside the field.
    fill(255, 255, 0, 150);
    // Left goal (for Blue to score; Red defends):
    rect(-this.goalWidth, (this.h - this.goalHeight) / 2, this.goalWidth, this.goalHeight);
    // Right goal (for Red to score; Blue defends):
    rect(this.w, (this.h - this.goalHeight) / 2, this.goalWidth, this.goalHeight);
    noFill();
    
    // Draw bold goal posts.
    strokeWeight(4);
    // Left goal posts:
    stroke(0, 0, 255);
    line(0, (this.h - this.goalHeight) / 2, 0, (this.h + this.goalHeight) / 2);
    // Right goal posts:
    stroke(255, 0, 0);
    line(this.w, (this.h - this.goalHeight) / 2, this.w, (this.h + this.goalHeight) / 2);
    strokeWeight(1);
  }
}

//---------------------------------------------------------
// Ball Class: Handles ball movement, collisions, and dribbler logic
//---------------------------------------------------------
class Ball {
  constructor(x, y) {
    this.pos = createVector(x, y);
    this.vel = createVector(0, 0);
    this.radius = 10;
    // attachedTo refers to the robot that is currently "dribbling" the ball.
    this.attachedTo = null;
  }
  
  update() {
    if (this.attachedTo) {
      // Stick to the robot's dribbler.
      this.pos = this.attachedTo.getDribblerPos();
      this.vel.set(0, 0);
    } else {
      this.pos.add(this.vel);
      this.vel.mult(0.99);
      
      // Bounce off the top and bottom boundaries.
      if (this.pos.y - this.radius < 0) {
        this.pos.y = this.radius;
        this.vel.y *= -1;
      }
      if (this.pos.y + this.radius > height) {
        this.pos.y = height - this.radius;
        this.vel.y *= -1;
      }
      
      // Prevent the ball from going past the goal mouths.
      if (this.pos.x - this.radius < 0) {
        this.pos.x = this.radius;
        this.vel.x *= -1;
      }
      if (this.pos.x + this.radius > width) {
        this.pos.x = width - this.radius;
        this.vel.x *= -1;
      }
    }
  }
  
  // Reset the ball to the center.
  reset() {
    this.pos.set(width / 2, height / 2);
    this.vel.set(0, 0);
    this.attachedTo = null;
  }
  
  display() {
    fill(255);
    noStroke();
    ellipse(this.pos.x, this.pos.y, this.radius * 2);
  }
}

//---------------------------------------------------------
// Robot Class: Represents a soccer robot with turning, kicking, dribbling, and collision behavior
//---------------------------------------------------------
class Robot {
  constructor(x, y, team, role, algorithm) {
    this.pos = createVector(x, y);
    this.startPos = this.pos.copy(); // Store initial position.
    this.team = team;       // "red" or "blue"
    this.role = role;       // "attacker" or "defender"
    this.algorithm = algorithm; // Behavior function.
    this.radius = 20;
    this.angle = 0;         // Orientation in radians (initially facing right).
    this.startAngle = this.angle; // Store initial orientation.
    this.vel = createVector(0, 0);
    // Set maximum speed based on team.
    this.maxSpeed = (team === "red") ? redSpeed : blueSpeed;
    this.maxAngularSpeed = 0.05;
    // Dribbler is a circular area in front of the robot.
    this.dribblerOffset = this.radius;
    this.dribblerRadius = 10;
    
    // For defenders, define two patrol points.
    if (this.role === "defender") {
      this.patrolPoints = [
        createVector(x, y - 50),
        createVector(x, y + 50)
      ];
      this.currentPatrolTargetIndex = 0;
    }
  }
  
  // Resets the robot to its starting position and orientation.
  resetPosition() {
    this.pos = this.startPos.copy();
    this.angle = this.startAngle;
  }
  
  update() {
    // The algorithm returns an object with:
    //    target: a p5.Vector,
    //    kick: boolean,
    //    rotate: desired angular change (in radians)
    let command = this.algorithm(this, ball, field);
    
    // --- Kicking functionality ---
    if (command.kick && ball.attachedTo === this) {
      ball.attachedTo = null;
      let kickSpeed = 7;
      ball.vel = p5.Vector.fromAngle(this.angle).mult(kickSpeed);
    }
    
    // --- Turning functionality ---
    if (command.rotate !== 0) {
      let delta = constrain(command.rotate, -this.maxAngularSpeed, this.maxAngularSpeed);
      this.angle += delta;
    } else {
      let desiredAngle = p5.Vector.sub(command.target, this.pos).heading();
      let angleDiff = desiredAngle - this.angle;
      angleDiff = atan2(sin(angleDiff), cos(angleDiff));
      if (abs(angleDiff) > this.maxAngularSpeed) {
        this.angle += this.maxAngularSpeed * (angleDiff > 0 ? 1 : -1);
      } else {
        this.angle = desiredAngle;
      }
    }
    
    // --- Movement ---
    this.vel = p5.Vector.fromAngle(this.angle).mult(this.maxSpeed);
    this.pos.add(this.vel);
    
    // Defender pacing behavior.
    if (this.role === "defender") {
      let target = this.patrolPoints[this.currentPatrolTargetIndex];
      if (p5.Vector.dist(this.pos, target) < 5) {
        this.currentPatrolTargetIndex = (this.currentPatrolTargetIndex + 1) % this.patrolPoints.length;
      }
    }
    
    // --- Ball Collision & Dribbler Check ---
    if (!ball.attachedTo) {
      let d = p5.Vector.dist(this.pos, ball.pos);
      if (d < this.radius + ball.radius) {
        if (this.isBallInDribbler(ball)) {
          ball.attachedTo = this;
        } else {
          let overlap = (this.radius + ball.radius) - d;
          let collisionNormal = p5.Vector.sub(ball.pos, this.pos).normalize();
          ball.pos.add(collisionNormal.mult(overlap));
          ball.vel.add(this.vel.copy().mult(0.5));
        }
      }
    }
  }
  
  // Checks if the ball is within the dribbler area.
  isBallInDribbler(ball) {
    let dribblerPos = this.getDribblerPos();
    return p5.Vector.dist(dribblerPos, ball.pos) < this.dribblerRadius;
  }
  
  // Returns the dribbler position (in front of the robot).
  getDribblerPos() {
    return p5.Vector.add(this.pos, p5.Vector.fromAngle(this.angle).mult(this.dribblerOffset));
  }
  
  display() {
    // Draw the robot.
    stroke(0);
    strokeWeight(2);
    fill(this.team === "red" ? color(255, 0, 0) : color(0, 0, 255));
    ellipse(this.pos.x, this.pos.y, this.radius * 2);
    
    // Draw the orientation line.
    push();
    translate(this.pos.x, this.pos.y);
    rotate(this.angle);
    stroke(0);
    line(0, 0, this.radius, 0);
    pop();
    
    // Draw the dribbler area.
    let dp = this.getDribblerPos();
    noFill();
    stroke(0, 255, 0);
    ellipse(dp.x, dp.y, this.dribblerRadius * 2);
  }
}

//---------------------------------------------------------
// Attacking Algorithm:
// If not carrying the ball, target the ball.
// If carrying the ball, target the opponent's goal and kick when aligned or, if near the goal,
// sometimes kick even if not perfectly aligned.
//---------------------------------------------------------
function attackingAlgorithm(robot, ball, field) {
  if (ball.attachedTo !== robot) {
    return { target: ball.pos.copy(), kick: false, rotate: 0 };
  } else {
    let goalPos = (robot.team === "red") ? createVector(width, height / 2) : createVector(0, height / 2);
    let desiredAngle = p5.Vector.sub(goalPos, robot.pos).heading();
    let angleDiff = desiredAngle - robot.angle;
    angleDiff = atan2(sin(angleDiff), cos(angleDiff));
    let tolerance = 0.1;
    let kick = abs(angleDiff) < tolerance;
    
    console.log(abs(angleDiff), tolerance, kick)
    // Also, if near the goal, sometimes kick even if not perfectly aligned.
    if (p5.Vector.dist(robot.pos, goalPos) < 150 && random() < 0.2) {
      kick = true;
    }
    let rotateCommand = 0;
    if (!kick) {
      rotateCommand = robot.maxAngularSpeed * (angleDiff > 0 ? 1 : -1);
    }
    return { target: goalPos, kick: kick, rotate: rotateCommand };
  }
}

//---------------------------------------------------------
// Defender Algorithm: The defender paces between preset patrol points.
//---------------------------------------------------------
function defenderAlgorithm(robot, ball, field) {
  let target = robot.patrolPoints[robot.currentPatrolTargetIndex];
  return { target: target, kick: false, rotate: 0 };
}
