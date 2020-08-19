#ifndef _TRANSMITTER_H_
#define _TRANSMITTER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "stm32f4xx.h"
#include <stdarg.h>

void sendByte(USART_TypeDef *USARTx, const unsigned char nValue);
void sendData(USART_TypeDef *USARTx, const unsigned char nLength, ...);
void recvData(USART_TypeDef *USARTx, float *k1, float *k2, float *k3, float *k4);

void sendFloat(USART_TypeDef *USARTx, const float nValue);
float readFloat(const unsigned char nIndex);

typedef union {
    unsigned char byteValue[4];
    float floatValue;
} UNION_FloatTypeDef;

typedef struct {
    unsigned char nPreByte;
    unsigned char nCurByte;
    unsigned char nIndex;
    unsigned char nLength;
    unsigned char nStart;
    unsigned char nBuffer[64];
} STRUCT_VariableTypeDef;


#ifdef __cplusplus
}
#endif

#endif
