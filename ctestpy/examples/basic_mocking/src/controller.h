/**
 * Defines a simple interface to control a low level hardware component.
 */

#ifndef __CONTROLLER__
#define __CONTROLLER__

#define CONTROLLER_FAILURE 0x00
#define CONTROLLER_SUCCESS 0xFF

/**
 * API to power on the hardware.
 */
int power_on(void);

/**
 * API to power off the hardware.
 */
int power_off(void);

#endif /* __CONTROLLER__ */
