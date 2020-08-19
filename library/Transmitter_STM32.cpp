#include "Transmitter_STM32.h"

UNION_FloatTypeDef unionData;
STRUCT_VariableTypeDef Variable;

void sendByte(USART_TypeDef *USARTx, const unsigned char nValue) {
    USARTx->DR = nValue;
    while ((USARTx->SR & 0x40) == 0);
}

void sendData(USART_TypeDef *USARTx, const unsigned char nLength, ...) {
    va_list nArgs;

    sendByte(USARTx, 0xff);
    sendByte(USARTx, 0x55);
    sendByte(USARTx, nLength * 4);
    va_start(nArgs, nLength);
    for (int i = 0; i < nLength; i++) {
        sendFloat(USARTx, (float)va_arg(nArgs, double));
    }
    va_end(nArgs);
}

void recvData(USART_TypeDef *USARTx, float *k1, float *k2, float *k3, float *k4) {
    if ((USARTx->SR & 0x20) != 0) {
        Variable.nCurByte = USARTx->DR;
        if (Variable.nCurByte == 0x55 && Variable.nStart == 0) {
            if (Variable.nPreByte == 0xff) {
                Variable.nIndex = 1;
                Variable.nStart = 1;
            }
        }
        else {
            Variable.nPreByte = Variable.nCurByte;
            if (Variable.nStart == 1) {
                if (Variable.nIndex > 2) {
                    Variable.nLength--;
                }
                else if (Variable.nIndex == 2) {
                    Variable.nLength = Variable.nCurByte;
                }
                Variable.nBuffer[Variable.nIndex] = Variable.nCurByte;
            }
        }
        Variable.nIndex++;
        if (Variable.nIndex > 63) {
            Variable.nIndex = 0;
            Variable.nStart = 0;
        }
        if (Variable.nStart == 1 && Variable.nLength == 0 && Variable.nIndex > 3) {
            Variable.nIndex = 0;
            Variable.nStart = 0;
            switch (Variable.nBuffer[7]) {
                case 0x01: {
                    *k1 = readFloat(3);
                    break;
                }
                case 0x02: {
                    *k2 = readFloat(3);
                    break;
                }
                case 0x03: {
                    *k3 = readFloat(3);
                    break;
                }
                case 0x04: {
                    *k4 = readFloat(3);
                    break;
                }
                case 0x05: {
                    sendData(USARTx, 4, *k1, *k2, *k3, *k4);
                    break;
                }
            }
        }
    }
}

void sendFloat(USART_TypeDef *USARTx, const float nValue) {
    unionData.floatValue = nValue;
    sendByte(USARTx, unionData.byteValue[0]);
    sendByte(USARTx, unionData.byteValue[1]);
    sendByte(USARTx, unionData.byteValue[2]);
    sendByte(USARTx, unionData.byteValue[3]);
}

float readFloat(const unsigned char nIndex) {
    unionData.byteValue[0] = Variable.nBuffer[nIndex];
    unionData.byteValue[1] = Variable.nBuffer[nIndex + 1];
    unionData.byteValue[2] = Variable.nBuffer[nIndex + 2];
    unionData.byteValue[3] = Variable.nBuffer[nIndex + 3];
    return unionData.floatValue;
}
