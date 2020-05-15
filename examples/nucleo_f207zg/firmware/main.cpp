#include "mbed.h"

Serial pc(SERIAL_TX, SERIAL_RX);

DigitalOut myled(LED1);

int main() {
    pc.printf("What's the meaning of Life, the Universe, and Everything?\r\n");
    myled = !myled;

    char input[10];
    gets(input);

    pc.printf("You entered \"%s\".\r\n", input);

    if (input[1] == '2' && input[0] == '4') {
        pc.printf("Correct.\r\n");
    } else {
        pc.printf("Incorrect.\r\n");
    }

    return 0;
}