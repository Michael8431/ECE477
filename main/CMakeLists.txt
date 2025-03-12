idf_component_register(SRCS "hello_world_main.c"
                    PRIV_REQUIRES spi_flash esp_timer esp_driver_spi driver soc freertos hal
                    INCLUDE_DIRS "")
