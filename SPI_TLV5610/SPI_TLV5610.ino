/*!
   @file    SPI_TLV5610.ino
   @brief   Recvice data from the PC and transfer it to the scope.
   @author  Chia-Wei Fan
   @date    2020/08/04
*/

#define _SCOPE_PROCESS_
#ifdef _SCOPE_PROCESS_

#include <SPI.h>
#define SS_Pin 48

unsigned char nStart = 0, nPrevByte = 0, nCurrByte = 0, nCurrPos = 0, nDataLen = 0, nRecvBuffer[64];

union {
  byte byteValue[4];
  float floatValue;
} unionValue;

void parseData() {
  int nChannelShift = 0;      // "nChannelShift" is the offset value of the TLV5610 channel.
  int nDataCount = nRecvBuffer[2] / 4, i = 0;
  float nValues[nDataCount];  // "nValues" is an array that stores the received datas.
  for (i = 0; i < nDataCount; i++) {
    unionValue.byteValue[0] = nRecvBuffer[3 + i * 4];
    unionValue.byteValue[1] = nRecvBuffer[3 + i * 4 + 1];
    unionValue.byteValue[2] = nRecvBuffer[3 + i * 4 + 2];
    unionValue.byteValue[3] = nRecvBuffer[3 + i * 4 + 3];
    nValues[i] = unionValue.floatValue;
  }

  //==================================================
  
  // TODO: Operation on data. 
  // nValues[0] = (nValues[0] - MIN) * 5 / (MAX - MIN);


  //==================================================

  for (i = 0; i < nDataCount; i++) {
    DAC_5610(i + nChannelShift, nValues[i]);
  }
}

void DAC_5610(const int &ch, const float &transfer_value) {
  int value_HB, value_LB;
  float X;
  int Y, Z;
  X = (float)(transfer_value * 4095.0 / 5.0);
  Y = (int)X / 256;
  Z = (int)X % 256;
  value_HB = (ch << 4) | Y;
  value_LB = Z;
  SPI.beginTransaction(SPISettings(5000000, MSBFIRST, SPI_MODE1));
  digitalWrite(SS_Pin, LOW);
  SPI.transfer(value_HB); // send command byte
  SPI.transfer(value_LB); // send value (0~255)
  digitalWrite(SS_Pin, HIGH);
  SPI.endTransaction();
}

void setup() {
  Serial.begin(115200);
  SPI.begin();
  pinMode(SS_Pin, OUTPUT);
  for (int DAx = 0; DAx < 9; DAx++) {
    DAC_5610(DAx, 0);
  }
}

void loop() {
  if (Serial.available()) {
    nCurrByte = Serial.read();
    if (nCurrByte == 0x55 && nStart == 0) {
      if (nPrevByte == 0xff) {
        nCurrPos = 1;
        nStart = 1;
      }
    }
    else {
      nPrevByte = nCurrByte;
      if (nStart == 1) {
        if (nCurrPos == 2) {
          nDataLen = nCurrByte;
        } else if (nCurrPos > 2) {
          nDataLen--;
        }
        nRecvBuffer[nCurrPos] = nCurrByte;
      }
    }
    nCurrPos++;
    if (nCurrPos > 63) {
      nStart = 0;
      nCurrPos = 0;
    }
    if (nStart == 1 && nDataLen == 0 && nCurrPos > 3) {
      nStart = 0;
      nCurrPos = 0;
      parseData();
    }
  }
}

#endif

//*************************************************************//
//********                                             ********//
//********   The test program is under this comment.   ********//
//********                                             ********//
//*************************************************************//

//#define _SCOPE_TEST_
#ifdef _SCOPE_TEST_

void setup() {
  Serial.begin(115200);
  SPI.begin();
  pinMode(SS_Pin, OUTPUT);
  for (int i = 0; i < 9; i++) {
    DAC_5610(i, 0);
  }
}

void loop() {
  static float temp1, temp2, k;
  Serial.print(temp1), Serial.print("\t");
  Serial.print(temp2), Serial.print("\t");
  Serial.println(k);
  k = k + 0.003;

  temp1 = 2.5 * sin(k) + 2.5;
  temp2 = 2.5 * cos(k) + 2.5;

  DAC_5610(0, temp1); // (channel, float(0 ~ 5))
  DAC_5610(1, temp2);

  delay(1); 
}

#endif
