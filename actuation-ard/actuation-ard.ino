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

 if (Serial.available() >= BUFFER_SIZE) {
    // Read the data from the serial buffer
    Serial.readBytes(buffer, BUFFER_SIZE);
    // Convert the received data from char array to int
    receivedData = atoi(buffer);
 }


digitalWrite(LeftPin1, HIGH);
digitalWrite(RightPin1, LOW);
analogWrite(PWM_Pin1, receivedData);

  
}
