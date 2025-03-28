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


void send_rfid_packet() {
    printf("\nPretend This sends the packet for now\n");
}

static void on_picc_state_changed(void *arg, esp_event_base_t base, int32_t event_id, void *data)
{
    rc522_picc_state_changed_event_t *event = (rc522_picc_state_changed_event_t *)data;
    rc522_picc_t *picc = event->picc;

    if (picc->state == RC522_PICC_STATE_ACTIVE) {
        // rc522_picc_print(picc);
        (create_rfid_packet(picc));
        send_rfid_packet();
        // implement above later
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
            rc522_register_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc_state_changed, NULL);
            set_state(ACTIVE_PLACE);
            break;
        case ACTIVE_PLACE:
            rc522_unregister_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc_state_changed);
            set_state(ACTIVE_ROLE);
            break;
        case ACTIVE_ROLE:
            set_state(PASSIVE_DEFENSE);
            break;
        case PASSIVE_DEFENSE:
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
            return "PASSIVE DEFENSE";
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
        ESP_LOGI("BUTTON", "Button Pressed!");
        printf("State Changed from %s to %s\n", state_to_string(temp), 
        state_to_string(current_state));
        //Later implementation
        //  Send packet of new state over to PC via UART
    }
}


// Interrupt service routine (ISR) for the button press
static void IRAM_ATTR gpio_isr_handler(void* arg) {
    // Start the debounce timer (one-shot)
    esp_timer_start_once(debounce_timer, DEBOUNCE_TIME_MS * 1000); // Convert ms to microseconds
}


void app_main()
{
    //IS THIS SAFE???
    //vTaskSuspendAll();

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
                if(pc_is_ready) {
                    set_state(ACTIVE_PLACE);
                }
                break;
            case ACTIVE_PLACE:
                //RFID sensor is on for this entire state
                break;
            case ACTIVE_ROLE:
                //RFID sensor is turned off when switching into this state
                break;
            case PASSIVE_DEFENSE:
                loop = false; // temporary break out to avoid
                break;
        }
        // built-in delay of 100ms
        // avoiding watchdog reset
        // might not be necessary but afraid to disable the scheduler
        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
    // rc522_start(scanner);
    // rc522_stop(scanner);



}