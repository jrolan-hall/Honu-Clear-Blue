#include <dht.h>
#include <Servo.h>

dht DHT;
Servo CMO;    //comb motor
Servo DMO;    //door motor
Servo LMO;    //left motor
Servo RMO;    //right motor
int DSW;      //door switch
float SIR1;   //shell IR sensor 1
float SIR2;   //shell IR sensor 2
float SIR3;   //shell IR sensor 3
float FCLF;   //front cliff sensor
float BCLF;   //back cliff sensor
float TMP;    //temperature sensor
float HMD;    //humidity sensor
char temp;    //temporary character for serial read
String toprint = "Hello Pi";

void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT);  //door switch on pin 2
  pinMode(4, OUTPUT); //front LED on pin 4
  pinMode(7, OUTPUT); //left LED on pin 7
  pinMode(8, OUTPUT); //right LED on pin 8
  pinMode(10, OUTPUT); //back LED on pin 10
  CMO.attach(11);      //comb motor on PWM input 3
  LMO.attach(9);      //left motor on PWM input 5 (changed to door)
  RMO.attach(3);      //right motor on PWM input 6
  DMO.attach(5);      //door motor on PWM input 9 (changed to left)
}

void loop() {

  //get commands
  int end = 0;
  String command = "";
  while (end == 0)
  {
    if (Serial.available() > 0)
    {
      temp = Serial.read();
      if (temp != '\n')
      {
        command += temp;
      }
      else
      {
        end = 1;
      }
    }
    else
    {
      end = 1;
    }
  }

  int action = command.toInt();
  int action2 = 1500;

  //figure out what to do

  if ((action >= 1000) && (action <= 1999)) //both drive motors
  {
    LMO.writeMicroseconds(action);
    if (action > 1500)
    {
      RMO.writeMicroseconds(1500-(action-1500));
    }
    else if (action < 1500)
    {
      RMO.writeMicroseconds(1500+(1500-action));
    }
    else if (action == 1500)
    {
    RMO.writeMicroseconds(action);
    }
    Serial.println("DRIVE:" + command);
  }
  else if ((action >= 2000) && (action <= 2999)) //left motor
  {
    action2 = action - 1000;
    LMO.writeMicroseconds(action2);
    Serial.println("LMO:" + String(action2));
  }
  else if ((action >= 3000) && (action <= 3999)) //right motor
  {
    action2 = action - 2000;
    RMO.writeMicroseconds(action2);
    Serial.println("RMO:" + String(action2));
  }
  else if ((action >= 4000) && (action <= 4999)) //comb motor
  {
    action2 = action - 3000;
    CMO.writeMicroseconds(action2);
    Serial.println("CMO:" + String(action2));
  }
  else if ((action >= 5000) && (action <= 5999)) //door motor
  {
    action2 = action - 4000;
    DMO.writeMicroseconds(action2);
    Serial.println("DMO:" + String(action2));
  }
  else if (action == 6000) //lock position
  {
    digitalWrite(4, HIGH);
    digitalWrite(7, HIGH);
    digitalWrite(8, HIGH);
    digitalWrite(10, HIGH);
    CMO.writeMicroseconds(1500);
    LMO.writeMicroseconds(1500);
    RMO.writeMicroseconds(1500);
    DMO.writeMicroseconds(1500);
    Serial.println("LOCK:1");
  }
  else if (action == 6001) //turn on front LED
  {
    digitalWrite(4, HIGH);
    Serial.println("FLED:1");
  }
  else if (action == 6002) //turn off front LED
  {
    digitalWrite(4, LOW);
    Serial.println("FLED:0");
  }
  else if (action == 6003) //turn on left LED
  {
    digitalWrite(7, HIGH);
    Serial.println("LLED:1");
  }
  else if (action == 6004) //turn off left LED
  {
    digitalWrite(7, LOW);
    Serial.println("LLED:0");
  }
  else if (action == 6005) //turn on right LED
  {
    digitalWrite(8, HIGH);
    Serial.println("RLED:1");
  }
  else if (action == 6006) //turn off right LED
  {
    digitalWrite(8, LOW);
    Serial.println("RLED:0");
  }
  else if (action == 6007) //turn on back LED
  {
    digitalWrite(10, HIGH);
    Serial.println("BLED:1");
  }
  else if (action == 6008) //turn off back LED
  {
    digitalWrite(10, LOW);
    Serial.println("BLED:0");
  }
  else if (action == 6009) //send shell IR1 data
  {
    SIR1 = analogRead(1);
    toprint = "SIR1:" + String(SIR1, 2);
    Serial.println(toprint);
  }
  else if (action == 6010) //send shell IR2 data
  {
    SIR2 = analogRead(2);
    toprint = "SIR2:" + String(SIR2, 2);
    Serial.println(toprint);
  }
  else if (action == 6011) //send shell IR3 data
  {
    SIR3 = analogRead(3);
    toprint = "SIR3:" + String(SIR3, 2);
    Serial.println(toprint);
  }
  else if (action == 6012) //send door switch data
  {
    DSW = digitalRead(2);
    toprint = "DSW:" + String(DSW);
    Serial.println(toprint);
  }
  else if (action == 6013) //send front cliff sensor data
  {
    FCLF = analogRead(10);
    toprint = "FCLF:" + String(FCLF);
    Serial.println(toprint);
  }
  //  else if (action=6014) //send humidity data
  //    {
  //      HMD = DHT.humidity;
  //      toprint = "HMD:"+String(HMD);
  //      Serial.println(toprint);
  //    }
  //  else if (action=6015) //send temperature data
  //    {
  //      TMP = DHT.temperature;
  //      toprint = "TMP:"+String(TMP);
  //      Serial.println(toprint);
  //    }
  delay(2);
}
