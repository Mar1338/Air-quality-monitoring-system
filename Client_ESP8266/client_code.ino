#include <temp.pb.h>
#include <pb_common.h>
#include <pb.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include <stdio.h>

#include "ScioSense_ENS160.h"
#include <Adafruit_AHTX0.h>
#include <Wire.h>
#include <SHTC3.h>
#include <ESP8266WiFi.h>

const char* ssid     = "1234";
const char* password = "huitablya";

const char* addr     = "192.168.43.114";
const uint16_t port  = 55835;

WiFiClient client;

SHTC3 sensor(Wire);

Adafruit_AHTX0 aht;

int tempC;        //To store the temperature in C
int tempF;        //temp in F
int humidity;     //To store the humidity

ScioSense_ENS160      ens160(ENS160_I2CADDR_1);


// setup WIFI and sensor
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  delay(10);

  Serial.println();
  Serial.print("Setting up WIFI for SSID ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("WIFI connection failed, reconnecting...");
    delay(500);
  }

  Serial.println("");
  Serial.print("WiFi connected, ");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.println("Starting SHTC3 sensor...");

  sensor.begin();
  Wire.begin();

  Serial.println("------------------------------------------------------------");
  Serial.println("ENS160 - Digital air quality sensor");
  Serial.println();
  Serial.println("Sensor readout in standard mode");
  Serial.println();
  Serial.println("------------------------------------------------------------");
  delay(1000);

  Serial.print("ENS160...");
  ens160.begin();
  Serial.println(ens160.available() ? "done." : "failed!");
  if (ens160.available()) {
    // Print ENS160 versions
    Serial.print("\tRev: "); Serial.print(ens160.getMajorRev());
    Serial.print("."); Serial.print(ens160.getMinorRev());
    Serial.print("."); Serial.println(ens160.getBuild());
  
    Serial.print("\tStandard mode ");
    Serial.println(ens160.setMode(ENS160_OPMODE_STD) ? "done." : "failed!");
  }

  // AHT20 start
  Serial.println("Adafruit AHT10/AHT20 demo!");

  if (! aht.begin()) {
    Serial.println("Could not find AHT? Check wiring");
    while (1) delay(10);
  }
  Serial.println("AHT10 or AHT20 found");
  //AHT20 end
}


void loop() {
  digitalWrite(LED_BUILTIN, LOW);
  Serial.print("connecting to ");
  Serial.println(addr);

  if (!client.connect(addr, port)) {
    Serial.println("connection failed");
    Serial.println("wait 5 sec to reconnect...");
    delay(5000);
    return;
  }
  

  sensor.begin(true);
  sensor.sample();
  float hum = sensor.readHumidity();
  float tmp = sensor.readTempC();
  
  // if (isnan(hum) || isnan(tmp)) {
  //   Serial.println("failed to read sensor data");
  //   return;
  // }

  
  pb_TempEvent temp = pb_TempEvent_init_zero;
  temp.deviceId = 12;
  temp.eventId = 100;
  temp.Aqi = ens160.getAQI();
  temp.Tvoc = ens160.getTVOC();
  temp.eCo2 = ens160.geteCO2();

    ///// AHT20 start
  sensors_event_t humidity1, temp1; //Tim had to change to  humidity1
  aht.getEvent(&humidity1, &temp1);// populate temp and humidity objects with fresh data
  tempC = (temp1.temperature);
  tempF = (temp1.temperature)*1.8+32;
  humidity = (humidity1.relative_humidity);

  temp.humidity = humidity1.relative_humidity;
  temp.tempCel = temp1.temperature;

  sendTemp(temp);
  digitalWrite(LED_BUILTIN, HIGH);


  //Serial.print("Temperature: "); 
  //Serial.print((float)tempC); 
  //Serial.println(" degrees C");
  //Serial.print("Temperature: "); 
  //Serial.print(tempF); 
  //Serial.println(" degrees F");
  //Serial.print("Humidity: "); 
  //Serial.print(humidity); 
  //Serial.println("% rH");

  delay(1000);

    ///// AHT20 end

  if (ens160.available()) {

    // Give values to Air Quality Sensor.
    ens160.set_envdata(tempC, humidity);

    ens160.measure(true);
    ens160.measureRaw(true);
  
    //Serial.print("AQI: ");Serial.print(ens160.getAQI());Serial.print("\t");
    //Serial.print("TVOC: ");Serial.print(ens160.getTVOC());Serial.print("ppb\t");
    //Serial.print("eCO2: ");Serial.print(ens160.geteCO2());Serial.println("ppm\t");
    //Serial.print("R HP0: ");Serial.print(ens160.getHP0());Serial.print("Ohm\t");
    //Serial.print("R HP1: ");Serial.print(ens160.getHP1());Serial.print("Ohm\t");
    //Serial.print("R HP2: ");Serial.print(ens160.getHP2());Serial.print("Ohm\t");
    //Serial.print("R HP3: ");Serial.print(ens160.getHP3());Serial.println("Ohm");
  }
  
  delay(5000);
}

void sendTemp(pb_TempEvent e) 
{
  uint8_t buffer[128];
  pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));
  

  if (!pb_encode(&stream, pb_TempEvent_fields, &e)){
    Serial.println("failed to encode temp proto");
    Serial.println(PB_GET_ERROR(&stream));
    return;
  }
  Serial.println(stream.bytes_written);
  client.write(buffer, stream.bytes_written);
}