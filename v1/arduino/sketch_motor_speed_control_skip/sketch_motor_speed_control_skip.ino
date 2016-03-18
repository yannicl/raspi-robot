//Arduino PWM Speed Control
int E1 = 5; //motor 1 speed
int M1 = 4; //motor 1
int E2 = 6; //motor 2 speed
int M2 = 7; //motor 2
int FRAME_LENGTH = 15;
int FRAME_START = 'A';
int FRAME_STOP = 'S';

void setup()
{
   pinMode(M1,OUTPUT);
   pinMode(M2,OUTPUT);
   Serial.begin(57600);
}

void loop()
{
  if (Serial.available() >= FRAME_LENGTH)
  {
    if (Serial.available() >= FRAME_LENGTH * 2) {
      skipOneFrame();
    }
    seekFrameStart();
    processFrameContent(); 
    delay(52);
  } else {
    analogWrite(E1, 0);
    analogWrite(E2, 0);
    delay(1);
  }
}

void skipOneFrame() {
  while(Serial.available() > 0) {
    int c = Serial.read();
    if (c == FRAME_STOP) {
      return;
    }
  }
}

void seekFrameStart() {
  while(Serial.available() > 0) {
    int c = Serial.read();
    if (c == FRAME_START) {
      return;
    }
  }
}

void processFrameContent() {
  if (Serial.available() >= FRAME_LENGTH - 1) {
    Serial.read(); // ,
    int dir1 = Serial.parseInt(); // 0 or 1
    Serial.read(); // ,
    int speed1 = Serial.parseInt(); // 3 chars integer
    Serial.read(); // ,
    int dir2 = Serial.parseInt(); // 0 or 1
    Serial.read(); // ,
    int speed2 = Serial.parseInt();
    Serial.read(); // ,
    Serial.read(); // S
    
    digitalWrite(M1, 1-dir1); // direction
    analogWrite(E1, speed1); // speed 100 = very low
    digitalWrite(M2, dir2); // direction
    analogWrite(E2, speed2);
  }
}

