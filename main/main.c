#include <esp_log.h>
#include "rc522.h"
#include "driver/rc522_spi.h"
#include "rc522_picc.h"

// Timer Interrupt for State Change
#include <stdio.h>
#include "driver/gpio.h"
#include "esp_timer.h"
// #include "esp_log.h"

//MISC includes
#include <string.h>
#include <stdlib.h>

// IR Matrix includes
#include "driver/adc.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc_cal.h"

//UART
// #include "freertos/FreeRTOS.h"
// #include "freertos/task.h"
#include "driver/uart.h"
// #include "esp_log.h"


#define UART_NUM UART_NUM_0  // Use UART1 (like MicroPython)
// #define UART_NUM UART_NUM_0  // Use UART0 (like devboard USBC), 
//                                 uncomment set pins also
#define TX_PIN 8
#define RX_PIN 7
#define BUF_SIZE 1024

// void uart_tx_task(void *arg)
// {
//     const char *msg = "Hello from ESP32 via UART!\n";

//     while (1) {
//         uart_write_bytes(UART_PORT_NUM, msg, strlen(msg));
//         vTaskDelay(pdMS_TO_TICKS(2000));  // Send every 2 seconds
//     }
// }

// TaskHandle_t uartTxTaskHandle = NULL;


#define BUTTON_GPIO  4
#define DEBOUNCE_TIME_MS  100


static const char *TAG = "rc522-basic-example";

#define RC522_SPI_BUS_GPIO_MISO    (21)
#define RC522_SPI_BUS_GPIO_MOSI    (19)
#define RC522_SPI_BUS_GPIO_SCLK    (5)
#define RC522_SPI_SCANNER_GPIO_SDA (7)
#define RC522_SCANNER_GPIO_RST     (25) // soft-reset

typedef enum {
    RST,
    IDLE,
    ACTIVE_PLACE,
    ACTIVE_ROLE,
    PASSIVE_DEFENSE
} state_t;

volatile state_t current_state = RST;
volatile bool pc_is_ready = false;

volatile uint8_t rfid_packet[9];

volatile bool ir_matrix[6][8] = {{false, false, false, false, false, false, false, false},
{false, false, false, false, false, false, false, false},
{false, false, false, false, false, false, false, false},
{false, false, false, false, false, false, false, false},
{false, false, false, false, false, false, false, false},
{false, false, false, false, false, false, false, false}
};

// Array is 48 bytes
// Packet Header is 1 byte
// Current State is int(4 bytes)

volatile uint8_t ir_packet[53];

volatile uint8_t state_packet[5];


static rc522_spi_config_t driver_config = {
    .host_id = SPI3_HOST,
    .bus_config = &(spi_bus_config_t){
        .miso_io_num = RC522_SPI_BUS_GPIO_MISO,
        .mosi_io_num = RC522_SPI_BUS_GPIO_MOSI,
        .sclk_io_num = RC522_SPI_BUS_GPIO_SCLK,
    },
    .dev_config = {
        .spics_io_num = RC522_SPI_SCANNER_GPIO_SDA,
    },
    .rst_io_num = RC522_SCANNER_GPIO_RST,
};

static rc522_driver_handle_t driver;
static rc522_handle_t scanner;

void create_rfid_packet(const rc522_picc_t *picc) {
    //packet type 1 byte
    const uint8_t rfid_packet_header = 0x01;
    //current game state 4 bytes, cast to byte pointer
    uint8_t *bytePtr = (uint8_t *)&current_state;
    //UID is 4 bytes, so 4 uint8_t
    char uid_str[RC522_PICC_UID_STR_BUFFER_SIZE_MAX];
    rc522_picc_uid_to_str(&picc->uid, uid_str, sizeof(uid_str));
    uint8_t uid[4];
    int byte_index = 0;
    char *token = strtok(uid_str, " ");
    while (token != NULL) {
        // Convert each token (hex string) to a byte (uint8_t)
        uid[byte_index] = (uint8_t)strtol(token, NULL, 16);  // Convert hex to uint8_t
        token = strtok(NULL, " ");  // Get next byte (token)
        byte_index++;
    }
    rfid_packet[0] = rfid_packet_header;
    rfid_packet[1] = bytePtr[0];
    rfid_packet[2] = bytePtr[1];
    rfid_packet[3] = bytePtr[2];
    rfid_packet[4] = bytePtr[3];
    rfid_packet[5] = uid[0];
    rfid_packet[6] = uid[1];
    rfid_packet[7] = uid[2];
    rfid_packet[8] = uid[3];
    printf("\n");
    printf("New RFID Packet\n");
    printf("%d 1=RFID header\n", rfid_packet[0]);
    printf("%X %X %X %X(int)Current State\n", (unsigned int)bytePtr[0],(unsigned int)bytePtr[1],(unsigned int)bytePtr[2],(unsigned int)bytePtr[3]);
    printf("%X %X %X %X UID", (unsigned int)uid[0], (unsigned int)uid[1], (unsigned int)uid[2], (unsigned int)uid[3]);
    printf("\n");
}

void create_state_packet() {
    const uint8_t state_packet_header = 0x03;
    uint8_t *bytePtr = (uint8_t *)&current_state;
    state_packet[0] = state_packet_header;
    state_packet[1] = bytePtr[0];
    state_packet[2] = bytePtr[1];
    state_packet[3] = bytePtr[2];
    state_packet[4] = bytePtr[3];
    printf("\n");
    printf("New State Packet\n");
    printf("%d 3=STATE header\n", state_packet[0]);
    printf("%X %X %X %X(int)Current State\n", (unsigned int)state_packet[1],(unsigned int)state_packet[2],(unsigned int)state_packet[3],(unsigned int)state_packet[4]);
    printf("\n");
}

void create_ir_packet() {
    const uint8_t ir_packet_header = 0x02;
    uint8_t *bytePtr = (uint8_t *)&current_state;
    ir_packet[0] = ir_packet_header;
    ir_packet[1] = bytePtr[0];
    ir_packet[2] = bytePtr[1];
    ir_packet[3] = bytePtr[2];
    ir_packet[4] = bytePtr[3];
    int cur = 5;
    for(int i = 0; i < 6; i++) {
        for(int j = 0; j < 8; j++) {
            ir_packet[cur] = (uint8_t)ir_matrix[i][j];
            cur++;
        }
    }
    printf("\n");
    printf("New IR Packet\n");
}


void send_rfid_packet() {
    uart_write_bytes(UART_NUM, (const char *)rfid_packet, sizeof(rfid_packet));
}

void send_ir_packet() {
    uart_write_bytes(UART_NUM, (const char *)ir_packet, sizeof(ir_packet));
}

void send_state_packet() {
    uart_write_bytes(UART_NUM, (const char *)state_packet, sizeof(state_packet));
}

static void on_picc_state_changed(void *arg, esp_event_base_t base, int32_t event_id, void *data)
{
    rc522_picc_state_changed_event_t *event = (rc522_picc_state_changed_event_t *)data;
    rc522_picc_t *picc = event->picc;

    if (picc->state == RC522_PICC_STATE_ACTIVE) {
        (create_rfid_packet(picc));
        send_rfid_packet();
    }
    else if (picc->state == RC522_PICC_STATE_IDLE && event->old_state >= RC522_PICC_STATE_ACTIVE) {
        ESP_LOGI(TAG, "Card has been removed");
    }
}



void set_state(state_t new_state) {
    current_state = new_state;
}


void next_state() { //Logic for switching states via button press
    switch (current_state) {
        case RST:
            // Not a button toggled state, see other switch case below
            break;
        case IDLE:
            // Not a button toggled state, see other switch case below
            // pc_is_ready = true; //TEMPORARY PERMISSION OVERRIDE FOR TESTING
            
            esp_err_t temp = rc522_start(scanner);
            rc522_register_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc_state_changed, NULL);
            // xTaskCreate(uart_tx_task, "uart_tx_task", 2048, NULL, 10, &uartTxTaskHandle); //To start the task
            set_state(ACTIVE_PLACE);
            break;
        case ACTIVE_PLACE:
            rc522_pause(scanner);
            rc522_unregister_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc_state_changed);
            set_state(ACTIVE_ROLE);
            break;
        case ACTIVE_ROLE:
            rc522_start(scanner);
            rc522_register_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc_state_changed, NULL);
            set_state(PASSIVE_DEFENSE);
            break;
        case PASSIVE_DEFENSE:
            rc522_pause(scanner);
            rc522_unregister_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc_state_changed);
            set_state(IDLE);
            break;
    }
}


static esp_timer_handle_t debounce_timer;
volatile bool is_pressed = false;

char* state_to_string(state_t this_state) {
    switch(this_state) {
        case IDLE:
            return "IDLE";
        case RST:
            return "RST";
        case ACTIVE_PLACE:
            return "ACTIVE_PLACE";
        case ACTIVE_ROLE:
            return "ACTIVE_ROLE";
        case PASSIVE_DEFENSE:
            return "PASSIVE_DEFENSE";
        default:
            return "UNKNOWN";
    }
}

// Function to execute when the button press is confirmed after debouncing
void pressed_callback(void *arg) {
    if (gpio_get_level(BUTTON_GPIO) == 0) { // Check if button is still pressed
        is_pressed = true;  // Set flag (or call another function)
        state_t temp = current_state;
        next_state(); //Increments to state after
        // ESP_LOGI("BUTTON", "Button Pressed!");
        printf("State Changed from %s to %s\n", state_to_string(temp), 
        state_to_string(current_state));
        //Later implementation
        //  Send packet of new state over to PC via UART
        create_state_packet();
        send_state_packet();
    }
}


// Interrupt service routine (ISR) for the button press
static void IRAM_ATTR gpio_isr_handler(void* arg) {
    // Start the debounce timer (one-shot)
    esp_timer_start_once(debounce_timer, DEBOUNCE_TIME_MS * 1000); // Convert ms to microseconds
}

    // Notes from Journal about GPIOS
    // The Pins for ESP32 are:
    // reading input voltage of ir sensors:
    // left to right 1-8
    // GPIO32 - GPIO 39
    // outputting enable signals for each camp
    // left to right, top to bottom 1-6
    // GPIO12 - GPIO15, GPIO26 & GPIO27

void config_gpio_output(gpio_num_t num) {
    //gpio_num setup
    gpio_config_t gpio_config_out = {};
    gpio_config_out.intr_type = GPIO_INTR_DISABLE;
    gpio_config_out.mode = GPIO_MODE_OUTPUT; 
    gpio_config_out.pin_bit_mask = (1ULL<<num); //GPIO 12
    gpio_config_out.pull_down_en = GPIO_PULLDOWN_DISABLE;
    gpio_config_out.pull_up_en = GPIO_PULLUP_DISABLE;
    esp_err_t gpio_err = gpio_config(&gpio_config_out);
    assert(gpio_err == ESP_OK);
    // Make sure it is set to off by default
    gpio_set_level(num, 0);
}

// 0-7 is of type adc1_channel_t

esp_adc_cal_characteristics_t adc_chars;

void config_adc_pin(adc1_channel_t channel) {
    adc1_config_width(ADC_WIDTH_BIT_12);  // 0 - 4095
    adc1_config_channel_atten(channel, ADC_ATTEN_DB_11); // for 0-3.3V

    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12, 1100, &adc_chars);
}



// IR Sensor For the Card Matrix
void ir_reading() { // assume all pins are already configured
    // Failsafe to make sure nothing changes during boot
    vTaskDelay(pdMS_TO_TICKS(100)); // Wait for boot to complete


    // Set GPIO_output to high with below command
    // gpio_set_level(GPIO_NUM_12, 1); // Set GPIO12 to HIGH
    // Example reading at gpio32
    // ADC1_CHANNEL_4


    gpio_num_t gpio_channels[8] = {
        GPIO_NUM_35,GPIO_NUM_34,GPIO_NUM_33,GPIO_NUM_32,GPIO_NUM_36,
        GPIO_NUM_37,GPIO_NUM_38,GPIO_NUM_39
    };

    // GPIO_NUM_13,
    // GPIO_NUM_2,
    // GPIO_NUM_15,
    // GPIO_NUM_14,
    // GPIO_NUM_27,
    // GPIO_NUM_12
    gpio_num_t enables[6] = {
        GPIO_NUM_27,
        GPIO_NUM_12,
        GPIO_NUM_15,
        GPIO_NUM_14,
        GPIO_NUM_13,
        GPIO_NUM_2
    };
    bool was_change = false;

    for(int i = 0; i < 6; i++) { // for each Enable pin/gate volage
        // send an enable
        gpio_set_level(enables[i], 0);
        //TESTING FOR MEASURING DOES NOT MATTER
        vTaskDelay(pdMS_TO_TICKS(100)); // 100ms delay
        //  ^^might be unnecessary, depending on how fast the IR is
        for(int j = 0; j < 8; j++) { // for each ir sensor using that enable pin
            // if channels[j] == ADC2_CHANNEL_7
            // int raw = adc1_get_raw(channels[j]);
            int level = gpio_get_level(gpio_channels[j]);
            vTaskDelay(pdMS_TO_TICKS(10));
            bool card_was_placed = false;
            if(level == 1) {
                card_was_placed = true;
            }
            if(card_was_placed != ir_matrix[i][j]) { // If it is read as covered
                ir_matrix[i][j] = card_was_placed; // Update value as covered
                printf("enable %d, sensor %d VALUE CHANGED\n", i, j);
                was_change = true;
            }
            // vTaskDelay(pdMS_TO_TICKS(2000));
        }
        // shut it back off
        gpio_set_level(enables[i], 1);
    }

    if(was_change) {
        create_ir_packet();
        send_ir_packet();
        // Create IR packet
        // Send IR packet
    }
    vTaskDelay(100 / portTICK_PERIOD_MS);
}






void app_main()
{
    ESP_LOGI("HELLO", "THE MICRO IS ON");
    ESP_LOGW("HELLO", "THE MICRO IS ON");
    //IS THIS SAFE???
    //vTaskSuspendAll();

    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
    };
    
    
    // Apply UART settings
    ESP_ERROR_CHECK(uart_param_config(UART_NUM, &uart_config));
    
    //This uses the pins on the DevBoard.
    ESP_ERROR_CHECK(uart_set_pin(UART_NUM, TX_PIN, RX_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
    
    // Install UART driver
    ESP_ERROR_CHECK(uart_driver_install(UART_NUM, BUF_SIZE, BUF_SIZE, 0, NULL, 0));

    // Notes from Journal about GPIOS
    // The Pins for ESP32 are:
    // reading input voltage of ir sensors:
    // left to right 1-8
    // GPIO32 - GPIO 39
    // outputting enable signals for each camp
    // left to right, top to bottom 1-6
    // GPIO12 - GPIO15, GPIO26 & GPIO27

    //config these only once, setting is done during the loop
    config_gpio_output(GPIO_NUM_12);
    config_gpio_output(GPIO_NUM_13);
    config_gpio_output(GPIO_NUM_14);
    config_gpio_output(GPIO_NUM_15);
    config_gpio_output(GPIO_NUM_2);
    config_gpio_output(GPIO_NUM_27);
    gpio_set_level(GPIO_NUM_12, 1); //this turns it on
    gpio_set_level(GPIO_NUM_13, 1); //this turns it on
    gpio_set_level(GPIO_NUM_14, 1); //this turns it on
    gpio_set_level(GPIO_NUM_15, 1); //this turns it on
    gpio_set_level(GPIO_NUM_2, 1); //this turns it on
    gpio_set_level(GPIO_NUM_27, 1); //this turns it on


    esp_rom_gpio_pad_select_gpio(GPIO_NUM_32);
    gpio_set_direction(GPIO_NUM_32, GPIO_MODE_INPUT);
    esp_rom_gpio_pad_select_gpio(GPIO_NUM_33);
    gpio_set_direction(GPIO_NUM_33, GPIO_MODE_INPUT);
    esp_rom_gpio_pad_select_gpio(GPIO_NUM_34);
    gpio_set_direction(GPIO_NUM_34, GPIO_MODE_INPUT);
    esp_rom_gpio_pad_select_gpio(GPIO_NUM_35);
    gpio_set_direction(GPIO_NUM_35, GPIO_MODE_INPUT);
    esp_rom_gpio_pad_select_gpio(GPIO_NUM_36);
    gpio_set_direction(GPIO_NUM_36, GPIO_MODE_INPUT);
    esp_rom_gpio_pad_select_gpio(GPIO_NUM_37);
    gpio_set_direction(GPIO_NUM_37, GPIO_MODE_INPUT);
    esp_rom_gpio_pad_select_gpio(GPIO_NUM_38);
    gpio_set_direction(GPIO_NUM_38, GPIO_MODE_INPUT);
    esp_rom_gpio_pad_select_gpio(GPIO_NUM_39);
    gpio_set_direction(GPIO_NUM_39, GPIO_MODE_INPUT);

    // Create the RFID tag instantiation
    rc522_spi_create(&driver_config, &driver);
    rc522_driver_install(driver);

    rc522_config_t scanner_config = {
        .driver = driver,
    };

    rc522_create(&scanner_config, &scanner);
    rc522_start(scanner); // BOOTS UP THE SCANNER
    // Set scanner to identify tags that are being read with rc522_register_events
    // rc522_register_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc_state_changed, NULL);
    // rc522_unregister_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc_state_changed);

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << BUTTON_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,  // Enable internal pull-up resistor
        .intr_type = GPIO_INTR_NEGEDGE  // Falling edge interrupt
        // .pin_bit_mask = (1ULL << BUTTON_GPIO),
        // .mode = GPIO_MODE_INPUT,
        // .pull_up_en = GPIO_PULLUP_DISABLE,  // Enable internal pull-up resistor
        // .pull_down_en = GPIO_PULLDOWN_ENABLE,
        // .intr_type = GPIO_INTR_NEGEDGE  // Falling edge interrupt
    };
    gpio_config(&io_conf);

    esp_timer_create_args_t debounce_timer_args = {
        .callback = &pressed_callback,
        .arg = NULL,
        .name = "debounce_timer"
    };
    esp_timer_create(&debounce_timer_args, &debounce_timer);

    // Install ISR service and attach the interrupt
    gpio_install_isr_service(0);
    gpio_isr_handler_add(BUTTON_GPIO, gpio_isr_handler, NULL);

    // p#_role: 1 = ACTIVE, 2 = PASSIVE, -1 = UNSET
    // int p1_role = -1;
    // int p2_role = -1;
    volatile bool loop = true;
    
    while(loop) {
        switch (current_state) { //State machine Logic now that switching is handled
            case RST:
                // Set everything Back to Zero like its a brand new game
                // Not button toggled, just pushes to IDLE after
                set_state(IDLE);
                break;
            case IDLE:
                // not button toggled
                // determine who goes first either player1 or player2
                // either info received from PC or it decided itself

                // waiting for permission to leave from PC
                // if(pc_is_ready) {
                //     set_state(ACTIVE_PLACE);
                // }
                break;
            case ACTIVE_PLACE:
                ir_reading();
                //RFID sensor is on for this entire state
                break;
            case ACTIVE_ROLE:
                ir_reading();
                break;
            case PASSIVE_DEFENSE:
                ir_reading();
                break;
        }
        // built-in delay of 100ms
        // avoiding watchdog reset
        // might not be necessary but afraid to disable the scheduler
        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
    // if (uartTxTaskHandle != NULL) {
    //     vTaskDelete(uartTxTaskHandle);
    //     uartTxTaskHandle = NULL;
    // }
    // rc522_start(scanner);
    // rc522_stop(scanner);
    
}