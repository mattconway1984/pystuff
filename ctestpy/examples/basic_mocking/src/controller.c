/**
 * Implementation of some very basic functions that can be unit tested.
 *
 * These functions interface with methods defined in `gpio_driver.h`, for this
 * example, these methods will be generated by ctestpy as mocks and driven by
 * test scripts to verify this implementation satisfies its requirements.
 */

#include "controller.h"
#include "gpio_driver.h"
#include "gpio_driver_new.h"

int power_on(void)
{
    if (get_gpio(GPIO_POWER) == GPIO_HIGH)
    {
        /* Already powered on */
        return CONTROLLER_SUCCESS;
    }
    
    if (set_gpio(GPIO_POWER, GPIO_HIGH) == GPIO_SUCCESS)
    {
        /* Power on complete */
        return CONTROLLER_SUCCESS;
    }

    return CONTROLLER_FAILURE;
}

int power_off(void)
{
    if (get_gpio(GPIO_POWER) == GPIO_LOW)
    {
        /* Already powered off */
        return CONTROLLER_SUCCESS;
    }
    
    if (set_gpio(GPIO_POWER, GPIO_LOW) == GPIO_SUCCESS)
    {
        /* Power off complete */
        return CONTROLLER_SUCCESS;
    }

    return CONTROLLER_FAILURE;
}
