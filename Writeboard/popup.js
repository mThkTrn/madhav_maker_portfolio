window.onload=function(){var slider = document.getElementById('slider');}

points=[]
function setup() {
  /*  buttonchange = createButton('Change Color');
  buttonchange.position(200,19)
  buttonchange.mousePressed(changeColor)*/
  button = createButton('Change Canvas');
  button.position(19, 19);
  button.mousePressed(changeBG);
  buttonsave = createButton("Download");
  buttonsave.mousePressed(save);
  buttonsave.size(600)
  c=createCanvas(600,400)
  background(220)
  
}



function draw() {

  if (key=="b"){
    color="blue"
    
  }
  
  window.color="black"
  var size = 10
  stroke(color)
  fill(color)
  
  beginShape();
  for(let i = 0; i<points.length; i++){
    let x = points.x;
    let y = points.y;
    
    vertex(x,y)
  }
  endShape();
 
      if(mouseIsPressed){
  	stroke(color)
        strokeWeight(slider.value)
   line(mouseX,mouseY,pmouseX,pmouseY) 
  	}


}



function changeBG() {
  bcolor=window.prompt("what color do you want the new canvas to be","white")
  setTimeout(function(){ background(bcolor.toLowerCase()); }, 100);
}

function save() {
  saveCanvas(c, 'myCanvas', 'jpg');
  
}

function changeColor(){
window.prompt("what color do you want your brush","")
  
}
