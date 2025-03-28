// // /*
// //  * SPDX-FileCopyrightText: 2010-2022 Espressif Systems (Shanghai) CO LTD
// //  *
// //  * SPDX-License-Identifier: CC0-1.0
// //  */

// //esp_timer imports
// #include <stdio.h>
// #include <string.h>
// #include <unistd.h>
// #include "esp_timer.h"
// #include "esp_log.h"
// #include "esp_sleep.h"
// #include "sdkconfig.h"

// //uart
// #include "driver/uart.h"
// #include "freertos/FreeRTOS.h"
// #include "freertos/task.h"
// #include "esp_log.h"
// #include <string.h>
// #include "run_rfid.c"

// // #define UART_NUM UART_NUM_1  // Use UART1 (like MicroPython)
// #define UART_NUM UART_NUM_0  // Use UART0 (like devboard USBC), 
// //                                 uncomment set pins also
// #define TX_PIN 8
// #define RX_PIN 7
// #define BUF_SIZE 1024

// static void uart_receieve_task(void *arg) {
//     uart_port_t uart_num = UART_NUM;  // Using UART2

//     uint8_t data[BUF_SIZE];
//     int length = 0;

//     while (1) {
//         // Check if data is available
//         length = uart_read_bytes(uart_num, data, BUF_SIZE, 100 / portTICK_PERIOD_MS);
//         if (length > 0) {
//             // Print received data
//             data[length] = '\0';  // Null-terminate the received data
//             ESP_LOGI("UART", "Received data: %s", data);
//         }
//         vTaskDelay(10 / portTICK_PERIOD_MS);  // Add a small delay to avoid hogging CPU
//     }
// }

// void uart_send_task(void *arg) {
//     const char *message = "Hello from ESP32!\n";  // Data to send

//     while (1) {
//         uart_write_bytes(UART_NUM, message, strlen(message));  // Send message
//         ESP_LOGI("UART", "Sent: %s", message);
//         vTaskDelay(pdMS_TO_TICKS(1000));  // Delay 1 second
//     }
// }

// void timer_callback(void* args) {
//     printf("5 Seconds passed\n");
//     // int x = 0;
// }

// void app_main(void) //THIS IS THE ENTRY POINT
// {
//     printf("Hello world!\n");
//     // Test creating 5 second timer
//     esp_timer_handle_t timer_1;
//     esp_timer_create_args_t timer_1_args = {
//         .callback = timer_callback,
//         .name = "5 Second Timer",
//     };
//     esp_timer_create(&timer_1_args, &timer_1);

//     //Start the actual timer for every 5 seconds
//     esp_timer_start_periodic(timer_1, 5000000);
//     // printf(esp_timer_is_active(timer_1));

//     for (int i = 0; i < 5; ++i) {
//         ESP_ERROR_CHECK(esp_timer_dump(stdout));
//         usleep(1000000); //sleep for 1 second, so 5 of these and it prints
//     }
//     // UART configuration
//     uart_config_t uart_config = {
//         .baud_rate = 115200,
//         .data_bits = UART_DATA_8_BITS,
//         .parity = UART_PARITY_DISABLE,
//         .stop_bits = UART_STOP_BITS_1,
//         .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
//     };

//     // Apply UART settings
//     ESP_ERROR_CHECK(uart_param_config(UART_NUM, &uart_config));


//     //This uses the pins on the DevBoard.
//     ESP_ERROR_CHECK(uart_set_pin(UART_NUM, TX_PIN, RX_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
//     //Comment this to use default pins
//     //      then set UART0 for UART_NUM (UNPLUG FLASHING FIRST, should work)
//     //AFTER TESTING
//     //  If I read all data over UART_0, the pc receieves the data
//     //  EVERYTHING THAT GETS PRINTED TO MONITOR DEVICE IS ALSO SENT OVER THE USBC
//     //  all prinf statements are sent, all bootloader commands
//     //  All error codes and ESP_LOGI() calls get sent


//     // Install UART driver
//     ESP_ERROR_CHECK(uart_driver_install(UART_NUM, BUF_SIZE, BUF_SIZE, 0, NULL, 0));

//     // while (1) { //Infinite Loop of sending data
//     //     const char *message = "Hello from ESP32!\n";
//     //     uart_write_bytes(UART_NUM, message, strlen(message));
//     //     ESP_LOGI("UART", "Sent: %s", message);
        
//     //     vTaskDelay(pdMS_TO_TICKS(1000)); // Send every 1 second
//     // }

//     // while (1) { //Infinite Loop of sending data
//     //     const char *message = "Hello from ESP32!\n";
//     //     uart_write_bytes(UART_NUM, message, strlen(message));
//     //     ESP_LOGI("UART", "Sent: %s", message);
//     //     vTaskDelay(pdMS_TO_TICKS(1000)); // Send every 1 second
//     // }

//     while (1) {
//         // Check if data is available
//         uart_port_t uart_num = UART_NUM;  // Using UART2

//         uint8_t data[BUF_SIZE];
//         int length = 0;
//         length = uart_read_bytes(uart_num, data, BUF_SIZE, 100 / portTICK_PERIOD_MS);
//         if (length > 0) {
//             // Print received data
//             data[length] = '\0';  // Null-terminate the received data
//             ESP_LOGI("UART", "Received data: %s", data);
//             //SOME KIND OF IDENTIFIER THAT DOESNT NEED MONITOR DEVICE TO WORK
//             //CANNOT MONITOR DEVICE WHILE SENDING OVER THE UART
//         }
//         vTaskDelay(10 / portTICK_PERIOD_MS);  // Add a small delay to avoid hogging CPU
//     }

// }