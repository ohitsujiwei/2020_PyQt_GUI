#ifdef __cplusplus
extern "C" {
#endif

#include "stm32f4xx.h"

#include "stdio.h"
#include "math.h"

#include "Transmitter_STM32.h"

#define SEND
#define RECV

int fputc(int data, FILE *file);
int fgetc(FILE *file);
void delayMs(unsigned int nMs);
void delayUs(unsigned int nUs);

void Serial2Init(unsigned int nBaudrate);
void Serial3Init(unsigned int nBaudrate);

#if defined(SEND)

void loop() {
    double temp1, temp2, k;
    Serial2Init(115200);
    Serial3Init(115200);
    while (1) {
        k += 0.1;
        temp1 = 2.5 * sin(k) + 2.5;
        temp2 = 2.5 * cos(k) + 2.5;
        sendData(USART3, 2, temp1, temp2);
        delayMs(50);
    }
}

#elif defined(RECV)

void loop() {
    float k1, k2, k3, k4;
    Serial2Init(115200);
    Serial3Init(115200);
    while (1) {
        printf("k1 = %.2f  ", k1);
        printf("k2 = %.2f  ", k2);
        printf("k3 = %.2f  ", k3);
        printf("k4 = %.2f\n", k4);
        delayMs(50);
    }
}

void USART3_IRQHandler() {
    if (USART_GetITStatus(USART3, USART_IT_RXNE) != RESET) {
        recvData(USART3, &k1, &k2, &k3, &k4);
    }
}

#endif

void Serial2Init(unsigned int nBaudrate) {
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);
    USART_InitTypeDef USART_InitStructure;
    USART_InitStructure.USART_BaudRate = nBaudrate;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No ;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
    USART_Init(USART2, &USART_InitStructure);
    USART_Cmd(USART2, ENABLE);

    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2 | GPIO_Pin_3;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
    GPIO_InitStructure.GPIO_Speed = GPIO_High_Speed;
    GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    GPIO_PinAFConfig(GPIOA, GPIO_PinSource2, GPIO_AF_USART2);
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource3, GPIO_AF_USART2);
}

void Serial3Init(unsigned int nBaudrate) {
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART3, ENABLE);
    USART_InitTypeDef USART_InitStructure;
    USART_InitStructure.USART_BaudRate = nBaudrate;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No ;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
    USART_Init(USART3, &USART_InitStructure);
    USART_Cmd(USART3, ENABLE);

    USART_ITConfig(USART3, USART_IT_RXNE, ENABLE);
    NVIC_EnableIRQ(USART3_IRQn);

    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOC, ENABLE);
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10 | GPIO_Pin_11;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
    GPIO_InitStructure.GPIO_Speed = GPIO_High_Speed;
    GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOC, &GPIO_InitStructure);

    GPIO_PinAFConfig(GPIOC, GPIO_PinSource10, GPIO_AF_USART3);
    GPIO_PinAFConfig(GPIOC, GPIO_PinSource11, GPIO_AF_USART3);
}

int fputc(int data, FILE *file) {
    USART_SendData(USART2, (uint16_t) data);
    while (USART_GetFlagStatus(USART2, USART_FLAG_TC) == RESET) ;
    return data;
}

int fgetc(FILE *file) {
    while (USART_GetFlagStatus(USART2, USART_FLAG_RXNE) == RESET) ;
    return USART_ReceiveData(USART2);
}

void delayUs(unsigned int nUs) {
    SysTick->LOAD = nUs * 2;
    SysTick->VAL = 0x00;
    SysTick->CTRL = 0x01;
    while (!(SysTick->CTRL & (1 << 16))) ;
    SysTick->CTRL = 0x00;
}

void delayMs(unsigned int nMs) {
    while (nMs--) delayUs(1000);
}

#ifdef __cplusplus
}
#endif

int main(void) {
    loop();
}
