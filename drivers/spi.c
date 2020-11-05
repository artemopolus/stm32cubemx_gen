void spi_full_base(void)
{
    LL_SPI_Enable(SPIx);
    return 0;
}
void spi_full_base_init(void)
{
#include <embox/unit.h>
}
void spi_half_base(void)
{
    LL_SPI_Enable(SPIx);
	LL_SPI_SetTransferDirection(SPIx,LL_SPI_HALF_DUPLEX_TX);
    return 0;
}
void spi_half_base_init(void)
{
#include <embox/unit.h>
}

uint8_t spi_half_base_get_option(const uint8_t address)
{
    uint8_t value = address | 0x80;
	// remember to reset CS --> LL_GPIO_ResetOutputPin(GPIOA, LL_GPIO_PIN_4);
	while(!LL_SPI_IsActiveFlag_TXE(SPIx));
	LL_SPI_TransmitData8(SPIx, value);
	while(!LL_SPI_IsActiveFlag_TXE(SPIx));
	while(LL_SPI_IsActiveFlag_BSY(SPIx));
	LL_SPI_SetTransferDirection(SPIx,LL_SPI_HALF_DUPLEX_RX);
	while(!LL_SPI_IsActiveFlag_RXNE(SPIx));
	uint8_t result = 0;
	result = LL_SPI_ReceiveData8(SPIx);
	LL_SPI_SetTransferDirection(SPIx,LL_SPI_HALF_DUPLEX_TX);
	// remember to set CS --> LL_GPIO_SetOutputPin(GPIOA, LL_GPIO_PIN_4);
    return result;
}
uint8_t spi_half_base_set_option(const uint8_t address, const uint8_t value)
{
    uint8_t mask = 0x7F ;//01111111b
	mask &= address;
    // remember to reset CS -->LL_GPIO_ResetOutputPin(GPIOA, LL_GPIO_PIN_4);
    while(!LL_SPI_IsActiveFlag_TXE(SPIx));
    LL_SPI_TransmitData8(SPIx, mask);
    while(!LL_SPI_IsActiveFlag_TXE(SPIx));
	LL_SPI_TransmitData8(SPIx, value);
	while(!LL_SPI_IsActiveFlag_TXE(SPIx));
	while(LL_SPI_IsActiveFlag_BSY(SPIx));
	// remember to set CS -->LL_GPIO_SetOutputPin(GPIOA,LL_GPIO_PIN_4);
    return 0;
}
void spi_full_dma(void)
{
    LL_DMA_ConfigAddresses(DMAx,
                           LL_DMA_CHANNEL_Rx,
                           LL_SPI_DMA_GetRegAddr(SPIx), (uint32_t)name_rx_buffer.dt_buffer,
                           LL_DMA_GetDataTransferDirection(DMAx, LL_DMA_CHANNEL_Rx));
    LL_DMA_SetDataLength(DMAx, LL_DMA_CHANNEL_Rx, name_rx_buffer.dt_count);

    LL_DMA_ConfigAddresses(DMAx,
                           LL_DMA_CHANNEL_Tx, (uint32_t)name_tx_buffer.dt_buffer,
                           LL_SPI_DMA_GetRegAddr(SPIx),
                           LL_DMA_GetDataTransferDirection(DMAx, LL_DMA_CHANNEL_Tx));
    LL_DMA_SetDataLength(DMAx, LL_DMA_CHANNEL_Tx, name_tx_buffer.dt_count);


    LL_DMA_EnableIT_TC(DMAx, LL_DMA_CHANNEL_Rx);
    LL_DMA_EnableIT_TE(DMAx, LL_DMA_CHANNEL_Rx);
    LL_DMA_EnableIT_TC(DMAx, LL_DMA_CHANNEL_Tx);
    LL_DMA_EnableIT_TE(DMAx, LL_DMA_CHANNEL_Tx);

    irq_attach(TX_NUM_IRQ, name_tx_irq_handler, 0, NULL, "name_irq_handler");
    irq_attach(RX_NUM_IRQ, name_rx_irq_handler, 0, NULL, "name_irq_handler");

    lthread_init(&name_tx_buffer.dt_lth, &name_tx_handler);
    lthread_init(&name_rx_buffer.dt_lth, &name_rx_handler);

    LL_SPI_EnableDMAReq_RX(SPIx);
    LL_SPI_EnableDMAReq_TX(SPIx);
    LL_SPI_Enable(SPIx);
    LL_DMA_EnableChannel(DMAx, LL_DMA_CHANNEL_Rx);
    return 0;
}
void spi_full_dma_init(void)
{
#include <errno.h>
#include <embox/unit.h>
#include <kernel/irq.h>
#include <kernel/lthread/lthread.h>
#include <kernel/lthread/sync/mutex.h>
#define name_RXTX_BUFFER_SIZE 5
typedef struct
{
    uint8_t dt_buffer[name_RXTX_BUFFER_SIZE];
    uint8_t dt_count;
    struct mutex dt_mutex;
    struct lthread dt_lth;
} name_buffer;

static name_buffer name_rx_buffer = {
    .dt_count = name_RXTX_BUFFER_SIZE,
};
static name_buffer name_tx_buffer = {
    .dt_count = name_RXTX_BUFFER_SIZE,
};
static irq_return_t name_tx_irq_handler(unsigned int irq_nr, void *data);
static irq_return_t name_rx_irq_handler(unsigned int irq_nr, void *data);
static int name_rx_handler(struct lthread *self);
static int name_tx_handler(struct lthread *self);
}

static irq_return_t spi_full_dma_tx_irq_handler(unsigned int irq_nr, void *data)
{
    if (LL_DMA_IsActiveFlag_TCx(DMAx) != RESET)
    {
        LL_DMA_ClearFlag_GIx(DMAx);
        lthread_launch(&name_tx_buffer.dt_lth);
    }
    return IRQ_HANDLED;
}
static irq_return_t spi_full_dma_rx_irq_handler(unsigned int irq_nr, void *data)
{
    if (LL_DMA_IsActiveFlag_TCx(DMAx) != RESET)
    {
        LL_DMA_ClearFlag_GIx(DMAx);
        lthread_launch(&name_rx_buffer.dt_lth);
    }
    return IRQ_HANDLED;
}
static int spi_full_dma_rx_handler(struct lthread *self)
{
    /* do when get data */
    return 0;
}
static int spi_full_dma_tx_handler(struct lthread *self)
{
    /* do after data sending */
    return 0;
}
uint8_t spi_full_dma_transmit(uint8_t *data, uint8_t datacount)
{
    if (datacount > name_RXTX_BUFFER_SIZE)
        return 1;
    LL_DMA_DisableChannel(DMAx, LL_DMA_CHANNEL_Tx);

    for (uint8_t i = 0; i < datacount; i++)
    {
        /* копирование данных */
        name_tx_buffer.dt_buffer[i] = data[i];
    }

    LL_DMA_SetDataLength(DMAx, LL_DMA_CHANNEL_Tx, datacount);
    LL_DMA_EnableChannel(DMAx, LL_DMA_CHANNEL_Tx);
    return 0;
}
uint8_t spi_full_dma_receive(uint8_t *data, uint8_t datacount)
{
    /* выполняем копирование из памяти */
    return 0;
}
uint8_t spi_full_dma_setdatalength( uint8_t datalength )
{
    LL_DMA_DisableChannel(DMAx, LL_DMA_CHANNEL_Rx);
    LL_DMA_SetDataLength(DMAx, LL_DMA_CHANNEL_Rx, datalength);
    LL_DMA_EnableChannel(DMAx, LL_DMA_CHANNEL_Rx);
    return 0;
}
