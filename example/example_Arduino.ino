/*!
 * @file    Transmitter.ino
 * @brief   Example of sending and receiving data from robot to PC.
 * @author  Chia-Wei Fan
 * @date    2020/07/24
 */

//#define _TRANSFER_ROBOT_DATA_
#ifdef _TRANSFER_ROBOT_DATA_

#include "Transmitter.h"
#include "SoftwareSerial.h"

SoftwareSerial softSerial(10, 11);

void setup() {
  Serial.begin(115200);
  Serial3.begin(115200);
  softSerial.begin(38400);
}

float v1 = 1.2, v2 = 3.4, v3 = 5.6;
float k1 = 0.1, k2 = 0.2, k3 = 0.3, k4 = 0.4;

void loop() {
  //====================================================================================================

  /*!
     @brief               Transfer data from robot to PC
     @param[in]   usart   The serial port to be used.
                          If using Softserial, the baudrate MUST BE "38400".
     @param[in]   count   Number of datas to send.
     @param[in]   value1  The 1st "FLOAT" data to be transmitted.
     @param[in]   value2  The 2nd "FLOAT" data to be transmitted.
     @param[in]   ...     More datas.
     @notice              There is no upper limit on the number of datas.
                          But too many datas will affect the stability.
  */
  /* sendData(usart, count, value1, value2, ...); */
  sendData(Serial3, 3, v1, v2, v3);
  sendData(softSerial, 5, v1, v2, v3, 7.8, -9.1);

  //====================================================================================================

  /*!
     @brief               Transfer data from robot to PC
     @param[in]   usart   The serial port to be used.
                          If using Softserial, the baudrate MUST BE "38400".
     @param[in]   value1  The 1st "FLOAT" paramter to be transmitted.
     @param[in]   value2  The 2nd "FLOAT" paramter to be transmitted.
     @param[in]   value3  The 3rd "FLOAT" paramter to be transmitted.
     @param[in]   value4  The 4th "FLOAT" paramter to be transmitted.
     @notice              Be sure to give all parameters when calling the function
  */
  /* recvData(usart, value1, value2, value3, value4); */
  recvData(Serial3, k1, k2, k3, k4);
  recvData(softSerial, k1, k2, k3, k4);

  //====================================================================================================
}

#else

//*************************************************************//
//********                                             ********//
//********   The test program is under this comment.   ********//
//********                                             ********//
//*************************************************************//

#include "Transmitter.h"
#include "SoftwareSerial.h"

SoftwareSerial softSerial(10, 11);

void setup() {
  Serial.begin(115200);
  Serial3.begin(115200);
  softSerial.begin(38400);
}

void loop() {
  if (0) {
    static float temp1, temp2, k;
    k = k + 0.003;
    temp1 = 2.5 * sin(k) + 2.5;
    temp2 = 2.5 * cos(k) + 2.5;
    sendData(Serial3, 2, temp1, temp2);
  }
  else {
    static float k1, k2, k3, k4;
    recvData(Serial3, k1, k2, k3, k4);
    Serial.print("k1= "), Serial.print(k1), Serial.print("  ");
    Serial.print("k2= "), Serial.print(k2), Serial.print("  ");
    Serial.print("k3= "), Serial.print(k3), Serial.print("  ");
    Serial.print("k4= "), Serial.print(k4), Serial.print("\n");
  }
//  delay(50);
}

#endif
