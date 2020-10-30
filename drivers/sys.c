void sys_init()
{
#include <assert.h>
#include <stdint.h>

#include <hal/arch.h>
#include <hal/clock.h>

#include <system_stm32xxxx.h>
#include <stm32xxxx_hal.h>
#include <stm32xxxx_hal_cortex.h>
#include "stm32xxxx_hal_uart.h"
#include <string.h>
#include <framework/mod/options.h>
#include <module/embox/arch/system.h>
}
void Error_Handler()
{
  while(1);
}

void arch_init(void) 
{

	SystemInit();
	HAL_Init();

	SystemClock_Config();
}

void arch_idle(void) 
{

}

void arch_shutdown(arch_shutdown_mode_t mode) 
{
	switch (mode) {
	case ARCH_SHUTDOWN_MODE_HALT:
	case ARCH_SHUTDOWN_MODE_REBOOT:
	case ARCH_SHUTDOWN_MODE_ABORT:
	default:
		HAL_NVIC_SystemReset();
		break;
	}

	/* NOTREACHED */
	while(1) {

	}
}

uint32_t HAL_GetTick(void) 
{
	return clock_sys_ticks();
}
