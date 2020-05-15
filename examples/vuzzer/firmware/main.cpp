#include "mbed.h"

Serial pc(SERIAL_TX, SERIAL_RX);

int main () {
    char buf[20];
    gets(buf);

    if (buf[1] == 0xEF && buf[0] == 0xFD) {
        pc.printf("Passed first check.\r\n");
    } else {
        pc.printf("Failed first check.\r\n");
        exit(1);
    }

    if (buf[10] == '%' && buf[11] == '@') {
        pc.printf("Passed second check.\r\n");

        if (strncmp((const char *) &buf[15], "MAZE", 4) == 0) {
            pc.printf("Passed third check.\r\n");
        } else {
            pc.printf("Failed third check.\r\n");
            exit(1);
        }
    } else {
        pc.printf("Failed second check.\r\n");
        exit(1);
    }

    return 0;
}