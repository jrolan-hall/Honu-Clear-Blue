#include <TextFinder.h>
#include <Servo.h>
#include <dht.h>


dht DHT;
float hmd;      //humidity
float tmp;     //temperature
int D_SW;       //door switch
int S_IR1;      //shell IR sensor 1
int S_IR2;      //shell IR sensor 2
int S_IR3;      //shell IR sensor 3
int L_CLIFF;    //left cliff sensor
int R_CLIFF;    //right cliff sensor
float C_MO_V;   //voltage across comb
char temp;    //temporary character for serial read
Servo CIM_C;    //comb motor
Servo CIM_L;    //left motor
Servo CIM_R;    //right motor

 String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void setup() {
Serial.begin(9600);
pinMode(2, INPUT);  //DOOR switch
CIM_C.attach(3); //1st PWM input
CIM_L.attach(5); //2nd PWM input
CIM_R.attach(6); //3rd PWM input
pinMode(4, OUTPUT); //front LED
pinMode(7, OUTPUT); //left LED
pinMode(8, OUTPUT); //right LED
pinMode(10, OUTPUT); //back LED
pinMode(9, OUTPUT); //door relay (4th PWM input)
}

//checkiing the sensors
void loop() 
  {

  // temperature and humidity stuff
  hmd = DHT.humidity;
  tmp = DHT.temperature;

  //receptacle door
  D_SW = digitalRead(2);

  //is it full?
  S_IR1 = analogRead(1);
  S_IR2 = analogRead(2);
  S_IR3 = analogRead(3);

  //cliff sensors
  L_CLIFF = analogRead(4);
  R_CLIFF = analogRead(5);

  //comb voltage
  C_MO_V = analogRead(0);

  //Tell Pi
  String toprint = "HMD:"+String(hmd,2)+"|TMP:"+String(tmp,2)+"|D_SW:"+String(D_SW)+"|S_IR1:"+String(S_IR1)+"|S_IR2:"+String(S_IR2)+"|S_IR3:"+String(S_IR3)+"|L_CLIFF:"+String(L_CLIFF)+"|R_CLIFF:"+String(R_CLIFF)+"|C_MO_V:"+String(C_MO_V,3);
  
  Serial.println(toprint);

  //Ask Pi
  
  //get commands
  int end = 0;
  String command = "";
  while(end==0)
    {
    if (Serial.available() > 0) 
      {
      temp = Serial.read();
      if(temp!='&')
        {
        command += temp;
        }
      else
        {
        end=1;
        }
      }
     else
     {
      end=1;
     }
    }
          
  //separate commands
  String CMOstr = getValue(command, '|', 0);
  String LMOstr = getValue(command, '|', 1);
  String RMOstr = getValue(command, '|', 2);
  String DOORstr = getValue(command, '|', 3);
  String FLEDstr = getValue(command, '|', 4);
  String LLEDstr = getValue(command, '|', 5);   
  String RLEDstr = getValue(command, '|', 6);
  String BLEDstr = getValue(command, '|', 7);

  //get values from strings
  int CMO = CMOstr.toInt();
  int LMO = LMOstr.toInt();
  int RMO = RMOstr.toInt();
  int DOOR = DOORstr.toInt();
  int FLED = FLEDstr.toInt();
  int LLED = LLEDstr.toInt();
  int RLED = RLEDstr.toInt();
  int BLED = BLEDstr.toInt();

  //actuate motors
  CIM_C.writeMicroseconds(CMO);
  CIM_L.writeMicroseconds(LMO);
  CIM_R.writeMicroseconds(RMO);

  //actuate door


  //actuate LEDS
  if(FLED!=0)
  {
    digitalWrite(6, HIGH);
  }
  else
  {
    digitalWrite(6, LOW);
  }
    if(LLED!=0)
  {
    digitalWrite(7, HIGH);
  }
  else
  {
    digitalWrite(7, LOW);
  }
    if(RLED!=0)
  {
    digitalWrite(8, HIGH);
  }
  else
  {
    digitalWrite(8, LOW);
  }
    if(BLED!=0)
  {
    digitalWrite(9, HIGH);
  }
  else
  {
    digitalWrite(9, LOW);
  }
  
  delay(50);
}
