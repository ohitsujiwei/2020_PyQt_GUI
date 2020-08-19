#ifndef _TRANSMITTER_H_
#define _TRANSMITTER_H_

#include "Arduino.h"

void sendFloat(Stream &nSerial, const float &nValue);
float readFloat(const unsigned char &nIndex);
void sendData(Stream &nSerial, const unsigned char &nLength, ...);
void recvData(Stream &nSerial, float &, float &, float &, float &);

#endif
