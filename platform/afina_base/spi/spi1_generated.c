#include "stm32f7xx_hal.h"
#include "stm32f7xx_ll_dma.h"
#include "stm32f7xx.h"
#include "stm32f7xx_ll_i2c.h"
#include "stm32f7xx_hal.h"
#include "stm32f7xx_ll_spi.h"
#include "stm32f7xx_ll_usart.h"
#include "stm32f7xx_ll_rcc.h"
#include "stm32f7xx_ll_system.h"
#include "stm32f7xx_ll_gpio.h"
#include "stm32f7xx_ll_exti.h"
#include "stm32f7xx_ll_bus.h"
#include "stm32f7xx_ll_cortex.h"
#include "stm32f7xx_ll_utils.h"
#include "stm32f7xx_ll_pwr.h"
#include "spi1_generated.h"
#include <embox/unit.h>
#include <kernel/irq.h>
#include <kernel/lthread/lthread.h>
#include <kernel/lthread/sync/mutex.h>
#define SPI1_FULL_DMA_RXTX_BUFFER_SIZE 5
typedef struct
{
    uint8_t dt_buffer[RXTX_BUFFER_SIZE];
    uint8_t dt_count;
    struct mutex dt_mutex;
    struct lthread dt_lth;
} SPI1_FULL_DMA_buffer;

static SPI1_FULL_DMA_buffer SPI1_FULL_DMA_rx_buffer = {
    .dt_count = SPI1_FULL_DMA_RXTX_BUFFER_SIZE,
};
static SPI1_FULL_DMA_buffer SPI1_FULL_DMA_tx_buffer = {
    .dt_count = SPI1_FULL_DMA_RXTX_BUFFER_SIZE,
};
static irq_return_t SPI1_FULL_DMA_tx_irq_handler(unsigned int irq_nr, void *data);
static irq_return_t SPI1_FULL_DMA_rx_irq_handler(unsigned int irq_nr, void *data);
static int SPI1_FULL_DMA_rx_handler(struct lthread *self);
static int SPI1_FULL_DMA_tx_handler(struct lthread *self);
EMBOX_UNIT_INIT(SPI1_FULL_DMA_init);
static int SPI1_FULL_DMA_init(void)
{
  LL_SPI_InitTypeDef SPI_InitStruct = {0};

  LL_GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* Peripheral clock enable */
  LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_SPI1);

  LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
  /**SPI1 GPIO Configuration
  PB4   ------> SPI1_MISO
  PB3   ------> SPI1_SCK
  PB5   ------> SPI1_MOSI
  */
  GPIO_InitStruct.Pin = LL_GPIO_PIN_4;
  GPIO_InitStruct.Mode = LL_GPIO_MODE_ALTERNATE;
  GPIO_InitStruct.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
  GPIO_InitStruct.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
  GPIO_InitStruct.Pull = LL_GPIO_PULL_NO;
  GPIO_InitStruct.Alternate = LL_GPIO_AF_5;
  LL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = LL_GPIO_PIN_3;
  GPIO_InitStruct.Mode = LL_GPIO_MODE_ALTERNATE;
  GPIO_InitStruct.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
  GPIO_InitStruct.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
  GPIO_InitStruct.Pull = LL_GPIO_PULL_NO;
  GPIO_InitStruct.Alternate = LL_GPIO_AF_5;
  LL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = LL_GPIO_PIN_5;
  GPIO_InitStruct.Mode = LL_GPIO_MODE_ALTERNATE;
  GPIO_InitStruct.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
  GPIO_InitStruct.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
  GPIO_InitStruct.Pull = LL_GPIO_PULL_NO;
  GPIO_InitStruct.Alternate = LL_GPIO_AF_5;
  LL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /* SPI1 DMA Init */

  /* SPI1_RX Init */
  LL_DMA_SetChannelSelection(DMA2, LL_DMA_STREAM_0, LL_DMA_CHANNEL_3);

  LL_DMA_SetDataTransferDirection(DMA2, LL_DMA_STREAM_0, LL_DMA_DIRECTION_PERIPH_TO_MEMORY);

  LL_DMA_SetStreamPriorityLevel(DMA2, LL_DMA_STREAM_0, LL_DMA_PRIORITY_LOW);

  LL_DMA_SetMode(DMA2, LL_DMA_STREAM_0, LL_DMA_MODE_NORMAL);

  LL_DMA_SetPeriphIncMode(DMA2, LL_DMA_STREAM_0, LL_DMA_PERIPH_NOINCREMENT);

  LL_DMA_SetMemoryIncMode(DMA2, LL_DMA_STREAM_0, LL_DMA_MEMORY_INCREMENT);

  LL_DMA_SetPeriphSize(DMA2, LL_DMA_STREAM_0, LL_DMA_PDATAALIGN_BYTE);

  LL_DMA_SetMemorySize(DMA2, LL_DMA_STREAM_0, LL_DMA_MDATAALIGN_BYTE);

  LL_DMA_DisableFifoMode(DMA2, LL_DMA_STREAM_0);

  /* SPI1_TX Init */
  LL_DMA_SetChannelSelection(DMA2, LL_DMA_STREAM_3, LL_DMA_CHANNEL_3);

  LL_DMA_SetDataTransferDirection(DMA2, LL_DMA_STREAM_3, LL_DMA_DIRECTION_MEMORY_TO_PERIPH);

  LL_DMA_SetStreamPriorityLevel(DMA2, LL_DMA_STREAM_3, LL_DMA_PRIORITY_LOW);

  LL_DMA_SetMode(DMA2, LL_DMA_STREAM_3, LL_DMA_MODE_NORMAL);

  LL_DMA_SetPeriphIncMode(DMA2, LL_DMA_STREAM_3, LL_DMA_PERIPH_NOINCREMENT);

  LL_DMA_SetMemoryIncMode(DMA2, LL_DMA_STREAM_3, LL_DMA_MEMORY_INCREMENT);

  LL_DMA_SetPeriphSize(DMA2, LL_DMA_STREAM_3, LL_DMA_PDATAALIGN_BYTE);

  LL_DMA_SetMemorySize(DMA2, LL_DMA_STREAM_3, LL_DMA_MDATAALIGN_BYTE);

  LL_DMA_DisableFifoMode(DMA2, LL_DMA_STREAM_3);

  SPI_InitStruct.TransferDirection = LL_SPI_FULL_DUPLEX;
  SPI_InitStruct.Mode = LL_SPI_MODE_MASTER;
  SPI_InitStruct.DataWidth = LL_SPI_DATAWIDTH_4BIT;
  SPI_InitStruct.ClockPolarity = LL_SPI_POLARITY_LOW;
  SPI_InitStruct.ClockPhase = LL_SPI_PHASE_1EDGE;
  SPI_InitStruct.NSS = LL_SPI_NSS_SOFT;
  SPI_InitStruct.BaudRate = LL_SPI_BAUDRATEPRESCALER_DIV2;
  SPI_InitStruct.BitOrder = LL_SPI_MSB_FIRST;
  SPI_InitStruct.CRCCalculation = LL_SPI_CRCCALCULATION_DISABLE;
  SPI_InitStruct.CRCPoly = 7;
  LL_SPI_Init(SPI1, &SPI_InitStruct);
  LL_SPI_SetStandard(SPI1, LL_SPI_PROTOCOL_MOTOROLA);
  LL_SPI_EnableNSSPulseMgt(SPI1);

    LL_DMA_ConfigAddresses(DMA2,
                           LL_DMA_Stream_0,
                           LL_SPI_DMA_GetRegAddr(SPI1), (uint32_t)SPI1_FULL_DMA_rx_buffer.dt_buffer,
                           LL_DMA_GetDataTransferDirection(DMA2, LL_DMA_Stream_0));
    LL_DMA_SetDataLength(DMA2, LL_DMA_Stream_0, SPI1_FULL_DMA_rx_buffer.dt_count);

    LL_DMA_ConfigAddresses(DMA2,
                           LL_DMA_Stream_3, (uint32_t)SPI1_FULL_DMA_tx_buffer.dt_buffer,
                           LL_SPI_DMA_GetRegAddr(SPI1),
                           LL_DMA_GetDataTransferDirection(DMA2, LL_DMA_Stream_3));
    LL_DMA_SetDataLength(DMA2, LL_DMA_Stream_3, SPI1_FULL_DMA_tx_buffer.dt_count);


    LL_DMA_EnableIT_TC(DMA2, LL_DMA_Stream_0);
    LL_DMA_EnableIT_TE(DMA2, LL_DMA_Stream_0);
    LL_DMA_EnableIT_TC(DMA2, LL_DMA_Stream_3);
    LL_DMA_EnableIT_TE(DMA2, LL_DMA_Stream_3);

    irq_attach(59, SPI1_FULL_DMA_tx_irq_handler, 0, NULL, "SPI1_FULL_DMA_irq_handler");
    irq_attach(56, SPI1_FULL_DMA_rx_irq_handler, 0, NULL, "SPI1_FULL_DMA_irq_handler");

    lthread_init(&SPI1_FULL_DMA_tx_buffer.dt_lth, &SPI1_FULL_DMA_tx_handler);
    lthread_init(&SPI1_FULL_DMA_rx_buffer.dt_lth, &SPI1_FULL_DMA_rx_handler);

    LL_SPI_EnableDMAReq_RX(SPI1);
    LL_SPI_EnableDMAReq_TX(SPI1);
    LL_SPI_Enable(SPI1);
    LL_DMA_EnableChannel(DMA2, LL_DMA_Stream_0);

}
void SPI1_FULL_DMA_tx_irq_handler(unsigned int irq_nr, void *data)
{
    if (LL_DMA_IsActiveFlag_TC3(DMA2) != RESET)
    {
        LL_DMA_IsActiveFlag_TC3(DMA2);
        lthread_launch(&SPI1_FULL_DMA_tx_buffer.dt_lth);
    }
    return IRQ_HANDLED;
}
STATIC_IRQ_ATTACH(59, SPI1_FULL_DMA_tx_irq_handler, NULL);
void SPI1_FULL_DMA_rx_irq_handler(unsigned int irq_nr, void *data)
{
    if (LL_DMA_IsActiveFlag_TC0(DMA2) != RESET)
    {
        LL_DMA_IsActiveFlag_TC0(DMA2);
        lthread_launch(&SPI1_FULL_DMA_rx_buffer.dt_lth);
    }
    return IRQ_HANDLED;
}
STATIC_IRQ_ATTACH(56, SPI1_FULL_DMA_rx_irq_handler, NULL);
static int SPI1_FULL_DMA_tx_handler(struct lthread *self)
{
    /* do after data sending */
    return 0;
}
static int SPI1_FULL_DMA_rx_handler(struct lthread *self)
{
    /* do when get data */
    return 0;
}
uint8_t SPI1_FULL_DMA_transmit(uint8_t *data, uint8_t datacount)
{
    if (datacount > SPI_FULL_DMA_RXTX_BUFFER_SIZE)
        return 1;
    LL_DMA_DisableChannel(DMA2, LL_DMA_Stream_3);

    for (uint8_t i = 0; i < datacount; i++)
    {
        /* копирование данных */
        SPI_FULL_DMA_tx_buffer.dt_buffer[i] = data[i];
    }

    LL_DMA_SetDataLength(DMA2, LL_DMA_Stream_3, datacount);
    LL_DMA_EnableChannel(DMA2, LL_DMA_Stream_3);
    return 0;
}
uint8_t SPI1_FULL_DMA_receive(uint8_t *data, uint8_t datacount)
{
    /* выполняем копирование из памяти */
    return 0;
}
uint8_t SPI1_FULL_DMA_setdatalength( uint8_t datalength )
{
    LL_DMA_DisableChannel(DMA2, LL_DMA_Stream_0);
    LL_DMA_SetDataLength(DMA2, LL_DMA_Stream_0, datalength);
    LL_DMA_EnableChannel(DMA2, LL_DMA_Stream_0);
    return 0;
}
