#include "CertificateExample.h"
#include "crc32_simple.h"
#include "debug.h"
#include "mbed.h"

int DEBUG = 0;
Serial pc(SERIAL_TX, SERIAL_RX);

int main()
{
    // Create certificate tree.
    int result;
    ASN1_TYPE PKIX1Implicit88 = ASN1_TYPE_EMPTY;
    char errorDescription[ASN1_MAX_ERROR_DESCRIPTION_SIZE];
    result = asn1_array2tree(pkix_asn1_tab, &PKIX1Implicit88, errorDescription);
    if (result != ASN1_SUCCESS) {
        asn1_perror(result);
        pc.printf("%s", errorDescription);
        exit(1);
    }

    // Get input.
    char* der;
    int der_len = -1;
    if (!DEBUG) {
        // Read in der_len.
        pc.printf("How many bytes?\n");
        char input[10];
        gets(input);
        der_len = atoi(input);

        // Ensure der_len was set.
        if (der_len == -1) {
            pc.printf("der_len not set!");
            exit(1);
        }

        // Read in der.
        pc.printf("Reading in %d bytes...\n", der_len);
        der = (char*)malloc(der_len + 1);
        memset(der, 0, der_len + 1);
        fread(der, 1, der_len, stdin);
        der[der_len] = '\0';
    } else {
        pc.printf("How many bytes?\n");
        der_len = cert_len;
        pc.printf("Reading in %d bytes...\n", der_len);
        der = cert;
    }

    // Print CRC32.
    uint32_t crc = 0;
    crc32(der, der_len, &crc);
    pc.printf("CRC32: %08lx\n", crc);

    // Get certificate and cleanup.
    pc.printf("Getting certificate...\n");
    get_certificate(PKIX1Implicit88, (unsigned char*)der, der_len);
    asn1_delete_structure(&PKIX1Implicit88);
    pc.printf("Goodbye!\n");

    return 0;
}