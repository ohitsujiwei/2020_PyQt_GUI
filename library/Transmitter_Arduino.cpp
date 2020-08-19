#include "Transmitter.h"

union {
  byte byteValue[4];
  float floatValue;
} unionData;

boolean isAvailable = false;
unsigned char nPreByte = 0,
              nCurByte = 0,
              nIndex = 0,
              nLength = 0,
              nStart = 0,
              nBuffer[64];

void sendFloat(Stream &nSerial, const float &nValue) {
  unionData.floatValue = nValue;
  nSerial.write(unionData.byteValue[0]);
  nSerial.write(unionData.byteValue[1]);
  nSerial.write(unionData.byteValue[2]);
  nSerial.write(unionData.byteValue[3]);
}

float readFloat(const unsigned char &nIndex) {
  unionData.byteValue[0] = nBuffer[nIndex];
  unionData.byteValue[1] = nBuffer[nIndex + 1];
  unionData.byteValue[2] = nBuffer[nIndex + 2];
  unionData.byteValue[3] = nBuffer[nIndex + 3];
  return unionData.floatValue;
}

void sendData(Stream &nSerial, const unsigned char &nLength, ...) {
  va_list nArgs;

  nSerial.write(0xff);
  nSerial.write(0x55);
  nSerial.write(nLength * 4);

  va_start(nArgs, nLength);
  for (int i = 0; i < nLength; i++) {
    sendFloat(nSerial, va_arg(nArgs, double));
  }
  va_end(nArgs);
}

void recvData(Stream &nSerial, float &k1, float &k2, float &k3, float &k4) {
  isAvailable = false;
  if (nSerial.available() > 0) {
    isAvailable = true;
    nCurByte = nSerial.read();
  }
  if (isAvailable) {
    if (nCurByte == 0x55 && nStart == 0) {
      if (nPreByte == 0xff) {
        nIndex = 1;
        nStart = 1;
      }
    }
    else {
      nPreByte = nCurByte;
      if (nStart == 1) {
        if (nIndex == 2) {
          nLength = nCurByte;
        } else if (nIndex > 2) {
          nLength--;
        }
        nBuffer[nIndex] = nCurByte;
      }
    }
    nIndex++;
    if (nIndex > 63) {
      nIndex = 0;
      nStart = 0;
    }
    if (nStart == 1 && nLength == 0 && nIndex > 3) {
      nIndex = 0;
      nStart = 0;
      switch (nBuffer[7]) {
        case 0x01: {
            k1 = readFloat(3);
            break;
          }
        case 0x02: {
            k2 = readFloat(3);
            break;
          }
        case 0x03: {
            k3 = readFloat(3);
            break;
          }
        case 0x04: {
            k4 = readFloat(3);
            break;
          }
        case 0x05: {
            sendData(nSerial, 4, k1, k2, k3, k4);
            break;
          }
      }
    }
  }
}
