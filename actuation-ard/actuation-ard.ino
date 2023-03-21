 // arduino mega
int PWM_Pin1 = 6;
int LeftPin1 = 22;
int RightPin1 = 23;
 
//arduino uno
//int PWM_Pin1 = 6;
//int LeftPin1 = 13;
//int RightPin1 = 12;

int DutyCycle1 = 10;
int DutyCycle2 = 0;
int Freq = 0;
int Time1 = 0;
int val1 = 0; // Variable, um den gelesenen Wert zu speichern
int val2 = 0;
int TIME1 = 52000;
int TIME2 = 52000;
int count = 1;
char serialDutyCycle = 0;
const int BUFFER_SIZE = 3;
char buffer[BUFFER_SIZE];
int receivedData = 0;

bool polarity = 0;
bool discharge = 0;


void setup()
{
  Serial.begin(115200);      // Datenrate, auch im Serial Monitor einstellen
  Serial.setTimeout(1);


  pinMode(PWM_Pin1, OUTPUT); // Setzt den Pin als output.
  pinMode(LeftPin1, OUTPUT);
  pinMode(RightPin1, OUTPUT);

  pinMode(4, INPUT);
  pinMode(11, OUTPUT);
}

void loop()
{

if (Serial.available() >= 2) { // check if at least 2 bytes are available
    int receivedData = Serial.read(); // read first byte
    receivedData |= Serial.read() << 8; // read second byte and combine with first byte

}

// old code:
//  if (Serial.available() >= 3) {
//     // Read the data from the serial buffer
//     Serial.readBytes(buffer, BUFFER_SIZE);
//     // Convert the received data from char array to int
//     receivedData = atoi(buffer);
//  }



if (receivedData == 300){ //corresponds to left polarity
  polarity = 0;
}
else if (receivedData == 320){ //corresponds to right polarity
  polarity = 1;
}
else if(receivedData == 350) { // corresponds to the discharge bytes
  discharge = !discharge;
}

if(discharge){
  digitalWrite(LeftPin1, LOW);
  digitalWrite(RightPin1, LOW);
}
else{
  if(polarity){
    digitalWrite(LeftPin1, LOW);
    digitalWrite(RightPin1, HIGH);
  }
  else{
    digitalWrite(LeftPin1, HIGH);
    digitalWrite(RightPin1, LOW);
  }
}

if(receivedData <= 255 && receivedData >= 0)
  analogWrite(PWM_Pin1, receivedData); 
}
