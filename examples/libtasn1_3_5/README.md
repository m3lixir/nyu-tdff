# libtasn1_3_5

We are using GNU's Libtasn1, which is the ASN.1 library used by GnuTLS, p11-kit and some other packages [\[1\]](#references). Specifically, we are using [libtasn1_3_5](https://gitlab.com/gnutls/libtasn1/tree/libtasn1_3_5).

# Building

The following are modifications to the directions for building libtasn1_3_5 for the Nucleo-L152RE and Nucleo-F207ZG (please still refer to [`README-alpha`](https://gitlab.com/gnutls/libtasn1/-/blob/libtasn1_3_5/README-alpha) in libtasn1_3_5 for directions on building).

## Before Building

We limit the size of the `asn1_node_st` struct because the Nucleo-L152RE and the Nucleo-F207ZG do not have enough SRAM.

Change line `123` in `lib/libtasn1.h` to:

```c
#define ASN1_MAX_NAME_SIZE 15
```

While `pkix_asn1_tab.c` is included in this repository, you may choose to build it yourself. If you build it yourself, ensure that all `name` values (index 0) in `pkix_asn1_tab.c` are no larger than 15 bytes.

## Building

After `make bootstrap` but before `make`, rerun the `./configure` command with the following additional parameters:

```bash
$ CFLAGS="-ggdb -mcpu=cortex-m3 -mlittle-endian -mthumb -mthumb-interwork --specs=rdimon.specs" ./configure --enable-debug --prefix=$(pwd)/install --build=x86_64-pc-linux-gnu --host=arm-none-eabi
```

Then:

```bash
$ make
$ make install
```

# Linking

Although this is already done in this repository, if you need to link to libtasn1_3_5 from another program exported from the [Mbed Online Compiler](https://ide.mbed.com/compiler/), add/modify the following lines to `Makefile`:

```makefile
INCLUDE_PATHS += -I/path/to/libtasn1/install/include
LIBRARY_PATHS := -L../mbed/TARGET_NUCLEO_L152RE/TOOLCHAIN_GCC_ARM -L/path/to/libtasn1/install/lib
LIBRARIES := -lmbed -ltasn1
```

# Common Vulnerabilities and Exposures

According to NIST [\[2\]](#references), 8 CVE's have been assigned to libtasn1_3_5:

1. [CVE-2018-6003 ](https://nvd.nist.gov/vuln/detail/CVE-2018-6003) (`_asn1_decode_simple_ber` in `decoding.c`)
2. [CVE-2017-10790](https://nvd.nist.gov/vuln/detail/CVE-2017-10790) (`_asn1_check_identifier` in `parser_aux.c`)
3. [CVE-2016-4008 ](https://nvd.nist.gov/vuln/detail/CVE-2016-4008) (`_asn1_extract_der_octet` in `decoding.c`)
4. [CVE-2015-3622 ](https://nvd.nist.gov/vuln/detail/CVE-2015-3622) (`_asn1_extract_der_octet` in `decoding.c`)
5. [CVE-2015-2806 ](https://nvd.nist.gov/vuln/detail/CVE-2015-2806) (`asn1_der_decoding` in `decoding.c`)
6. [CVE-2014-3469 ](https://nvd.nist.gov/vuln/detail/CVE-2014-3469) (`asn1_read_value_type`, `asn1_read_value` in `element.c`)
7. [CVE-2014-3468 ](https://nvd.nist.gov/vuln/detail/CVE-2014-3468) (`asn1_get_bit_der` in `decoding.c`)
8. [CVE-2014-3467 ](https://nvd.nist.gov/vuln/detail/CVE-2014-3467) (multiple unspecified vulnerabilities in `decoding.c`)

# References

[1] https://www.gnu.org/software/libtasn1/  
[2] [cpe:/a:gnu:libtasn1:3.5](https://nvd.nist.gov/vuln/search/results?form_type=Advanced&cves=on&cpe_version=cpe%3a%2fa%3agnu%3alibtasn1%3a3.5)
