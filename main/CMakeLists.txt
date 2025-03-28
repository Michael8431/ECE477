

idf_component_register(
    SRCS "temp.c" "rfid.c" "main.c"  # Add your source files here
    PRIV_REQUIRES spi_flash esp_timer esp_driver_spi driver soc freertos hal  # Required components
)

set(EXTRA_COMPONENT_DIRS $ENV{IDF_PATH}/components/abobija/rc522)