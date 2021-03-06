/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2020 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under Ultimate Liberty license
  * SLA0044, the "License"; You may not use this file except in compliance with
  * the License. You may obtain a copy of the License at:
  *                             www.st.com/SLA0044
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"
#include "stm32f1xx_ll_dma.h"
#include "stm32f1xx_ll_i2c.h"
#include "stm32f1xx_ll_spi.h"
#include "stm32f1xx_ll_tim.h"
#include "stm32f1xx_ll_usart.h"
#include "stm32f1xx_ll_rcc.h"
#include "stm32f1xx_ll_bus.h"
#include "stm32f1xx_ll_system.h"
#include "stm32f1xx_ll_exti.h"
#include "stm32f1xx_ll_cortex.h"
#include "stm32f1xx_ll_utils.h"
#include "stm32f1xx_ll_pwr.h"
#include "stm32f1xx.h"
#include "stm32f1xx_ll_gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define sensor_LSM303AH_SPI1 1
#define sensor_ISM330_SPI1 1
#define sensor_BMP280_I2C2 1
#define LSM303AH_SPI1_CS_Pin GPIO_PIN_4
#define LSM303AH_SPI1_CS_GPIO_Port GPIOA
#define ISM330_SPI1_CS_Pin GPIO_PIN_0
#define ISM330_SPI1_CS_GPIO_Port GPIOB
#define LSM303_INT1_XL_Pin GPIO_PIN_1
#define LSM303_INT1_XL_GPIO_Port GPIOB
#define LSM303_MAG_INT_Pin GPIO_PIN_2
#define LSM303_MAG_INT_GPIO_Port GPIOB
#define MLINE_SPI2_CS_Pin GPIO_PIN_12
#define MLINE_SPI2_CS_GPIO_Port GPIOB
#define ISM330_INT1_Pin GPIO_PIN_8
#define ISM330_INT1_GPIO_Port GPIOA
#define ISM330_INT2_Pin GPIO_PIN_9
#define ISM330_INT2_GPIO_Port GPIOA
#define FreePin1_Pin GPIO_PIN_10
#define FreePin1_GPIO_Port GPIOA
/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
