/* Example interface (with basic definitions that can be mocked */

#ifndef __gpio_driver__
#define __gpio_driver__

#define GPIO_LOW 0x00
#define GPIO_HIGH 0xFF

#define GPIO_POWER 0x1a
#define GPIO_RESET 0x2b
#define GPIO_LED 0x3c

#define GPIO_FAILURE 0x00
#define GPIO_SUCCESS 0xFF

/* API to get the direction of a GPIO */
int get_gpio(int gpio);


#endif /*__gpio_driver__ */
