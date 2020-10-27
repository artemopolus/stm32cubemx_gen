/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
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

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
typedef StaticTask_t osStaticThreadDef_t;
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */

/* USER CODE END Variables */
/* Definitions for dataCollectTask */
osThreadId_t dataCollectTaskHandle;
const osThreadAttr_t dataCollectTask_attributes = {
  .name = "dataCollectTask",
  .priority = (osPriority_t) osPriorityBelowNormal,
  .stack_size = 128 * 4
};
/* Definitions for sensorTask */
osThreadId_t sensorTaskHandle;
const osThreadAttr_t sensorTask_attributes = {
  .name = "sensorTask",
  .priority = (osPriority_t) osPriorityLow,
  .stack_size = 128 * 4
};
/* Definitions for spiTxMlineTask */
osThreadId_t spiTxMlineTaskHandle;
uint32_t spiTxMlineTaskBuffer[ 128 ];
osStaticThreadDef_t spiTxMlineTaskControlBlock;
const osThreadAttr_t spiTxMlineTask_attributes = {
  .name = "spiTxMlineTask",
  .stack_mem = &spiTxMlineTaskBuffer[0],
  .stack_size = sizeof(spiTxMlineTaskBuffer),
  .cb_mem = &spiTxMlineTaskControlBlock,
  .cb_size = sizeof(spiTxMlineTaskControlBlock),
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for spiRxMlineTask */
osThreadId_t spiRxMlineTaskHandle;
uint32_t spiRxMlineTaskBuffer[ 128 ];
osStaticThreadDef_t spiRxMlineTaskControlBlock;
const osThreadAttr_t spiRxMlineTask_attributes = {
  .name = "spiRxMlineTask",
  .stack_mem = &spiRxMlineTaskBuffer[0],
  .stack_size = sizeof(spiRxMlineTaskBuffer),
  .cb_mem = &spiRxMlineTaskControlBlock,
  .cb_size = sizeof(spiRxMlineTaskControlBlock),
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for uartTxTask */
osThreadId_t uartTxTaskHandle;
uint32_t UartTxTaskBuffer[ 128 ];
osStaticThreadDef_t UartTxTaskControlBlock;
const osThreadAttr_t uartTxTask_attributes = {
  .name = "uartTxTask",
  .stack_mem = &UartTxTaskBuffer[0],
  .stack_size = sizeof(UartTxTaskBuffer),
  .cb_mem = &UartTxTaskControlBlock,
  .cb_size = sizeof(UartTxTaskControlBlock),
  .priority = (osPriority_t) osPriorityAboveNormal,
};
/* Definitions for uartRxTask */
osThreadId_t uartRxTaskHandle;
uint32_t UartRxTaskBuffer[ 128 ];
osStaticThreadDef_t UartRxTaskControlBlock;
const osThreadAttr_t uartRxTask_attributes = {
  .name = "uartRxTask",
  .stack_mem = &UartRxTaskBuffer[0],
  .stack_size = sizeof(UartRxTaskBuffer),
  .cb_mem = &UartRxTaskControlBlock,
  .cb_size = sizeof(UartRxTaskControlBlock),
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for superVisorTask */
osThreadId_t superVisorTaskHandle;
uint32_t superVisorTaskBuffer[ 128 ];
osStaticThreadDef_t superVisorTaskControlBlock;
const osThreadAttr_t superVisorTask_attributes = {
  .name = "superVisorTask",
  .stack_mem = &superVisorTaskBuffer[0],
  .stack_size = sizeof(superVisorTaskBuffer),
  .cb_mem = &superVisorTaskControlBlock,
  .cb_size = sizeof(superVisorTaskControlBlock),
  .priority = (osPriority_t) osPriorityLow,
};

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */

/* USER CODE END FunctionPrototypes */

void startDataCollectTask(void *argument);
void startSensorTask(void *argument);
void startSpiTxMlineTask(void *argument);
void startSpiRxMlineTask(void *argument);
void startUartTxTask(void *argument);
void startUartRxTask(void *argument);
void startSuperVisorTask(void *argument);

void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/* Hook prototypes */
void configureTimerForRunTimeStats(void);
unsigned long getRunTimeCounterValue(void);

/* USER CODE BEGIN 1 */
/* Functions needed when configGENERATE_RUN_TIME_STATS is on */
__weak void configureTimerForRunTimeStats(void)
{

}

__weak unsigned long getRunTimeCounterValue(void)
{
return 0;
}
/* USER CODE END 1 */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of dataCollectTask */
  dataCollectTaskHandle = osThreadNew(startDataCollectTask, NULL, &dataCollectTask_attributes);

  /* creation of sensorTask */
  sensorTaskHandle = osThreadNew(startSensorTask, NULL, &sensorTask_attributes);

  /* creation of spiTxMlineTask */
  spiTxMlineTaskHandle = osThreadNew(startSpiTxMlineTask, NULL, &spiTxMlineTask_attributes);

  /* creation of spiRxMlineTask */
  spiRxMlineTaskHandle = osThreadNew(startSpiRxMlineTask, NULL, &spiRxMlineTask_attributes);

  /* creation of uartTxTask */
  uartTxTaskHandle = osThreadNew(startUartTxTask, NULL, &uartTxTask_attributes);

  /* creation of uartRxTask */
  uartRxTaskHandle = osThreadNew(startUartRxTask, NULL, &uartRxTask_attributes);

  /* creation of superVisorTask */
  superVisorTaskHandle = osThreadNew(startSuperVisorTask, NULL, &superVisorTask_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

}

/* USER CODE BEGIN Header_startDataCollectTask */
/**
  * @brief  Function implementing the dataCollectTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_startDataCollectTask */
void startDataCollectTask(void *argument)
{
  /* USER CODE BEGIN startDataCollectTask */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END startDataCollectTask */
}

/* USER CODE BEGIN Header_startSensorTask */
/**
* @brief Function implementing the sensorTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_startSensorTask */
void startSensorTask(void *argument)
{
  /* USER CODE BEGIN startSensorTask */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END startSensorTask */
}

/* USER CODE BEGIN Header_startSpiTxMlineTask */
/**
* @brief Function implementing the spiTxMlineTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_startSpiTxMlineTask */
void startSpiTxMlineTask(void *argument)
{
  /* USER CODE BEGIN startSpiTxMlineTask */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END startSpiTxMlineTask */
}

/* USER CODE BEGIN Header_startSpiRxMlineTask */
/**
* @brief Function implementing the spiRxMlineTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_startSpiRxMlineTask */
void startSpiRxMlineTask(void *argument)
{
  /* USER CODE BEGIN startSpiRxMlineTask */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END startSpiRxMlineTask */
}

/* USER CODE BEGIN Header_startUartTxTask */
/**
* @brief Function implementing the uartTxTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_startUartTxTask */
void startUartTxTask(void *argument)
{
  /* USER CODE BEGIN startUartTxTask */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END startUartTxTask */
}

/* USER CODE BEGIN Header_startUartRxTask */
/**
* @brief Function implementing the uartRxTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_startUartRxTask */
void startUartRxTask(void *argument)
{
  /* USER CODE BEGIN startUartRxTask */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END startUartRxTask */
}

/* USER CODE BEGIN Header_startSuperVisorTask */
/**
* @brief Function implementing the superVisorTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_startSuperVisorTask */
void startSuperVisorTask(void *argument)
{
  /* USER CODE BEGIN startSuperVisorTask */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END startSuperVisorTask */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */

/* USER CODE END Application */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
