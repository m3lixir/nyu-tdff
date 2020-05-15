/*
 * Copyright (C) 2000-2014 Free Software Foundation, Inc.
 *
 * This file is part of LIBTASN1.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

/*****************************************************/
/* File: CertificateExample.c                        */
/* Description: An example on how to use the ASN1    */
/*              parser with the Certificate.txt file */
/*****************************************************/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "libtasn1.h"


static char *
my_ltostr (long v, char *str)
{
  long d, r;
  char temp[20];
  int count, k, start;

  if (v < 0)
    {
      str[0] = '-';
      start = 1;
      v = -v;
    }
  else
    start = 0;

  count = 0;
  do
    {
      d = v / 10;
      r = v - d * 10;
      temp[start + count] = '0' + (char) r;
      count++;
      v = d;
    }
  while (v);

  for (k = 0; k < count; k++)
    str[k + start] = temp[start + count - k - 1];
  str[count + start] = 0;
  return str;
}

/******************************************************/
/* Function : get_name_type                           */
/* Description: analyze a structure of type Name      */
/* Parameters:                                        */
/*   char *root: the structure identifier             */
/*   char *answer: the string with elements like:     */
/*                 "C=US O=gov"                       */
/******************************************************/
static void
get_Name_type (ASN1_TYPE cert_def, ASN1_TYPE cert, const char *root,
           unsigned char *ans)
{
  int k, k2, result, len;
  char name[128], str[1024], str2[1024], name2[128], counter[5], name3[128];
  ASN1_TYPE value = ASN1_TYPE_EMPTY;
  char errorDescription[ASN1_MAX_ERROR_DESCRIPTION_SIZE];
  char *answer = (char *) ans;
  answer[0] = 0;
  k = 1;
  do
    {
      strcpy (name, root);
      strcat (name, ".AME.?");
      my_ltostr (k, counter);
      strcat (name, counter);
      len = sizeof (str) - 1;
      result = asn1_read_value (cert, name, str, &len);
      if (result == ASN1_ELEMENT_NOT_FOUND)
    break;
      k2 = 1;
      do
    {
      strcpy (name2, name);
      strcat (name2, ".?");
      my_ltostr (k2, counter);
      strcat (name2, counter);
      len = sizeof (str) - 1;
      result = asn1_read_value (cert, name2, str, &len);
      if (result == ASN1_ELEMENT_NOT_FOUND)
        break;
      strcpy (name3, name2);
      strcat (name3, ".APT");
      len = sizeof (str) - 1;
      result = asn1_read_value (cert, name3, str, &len);
      strcpy (name3, name2);
      strcat (name3, ".APO");
      if (result == ASN1_SUCCESS)
        {
          len = sizeof (str2) - 1;
          result =
        asn1_read_value (cert_def,
                 "AHU.AGD", str2,
                 &len);
          if (!strcmp (str, str2))
        {
          asn1_create_element (cert_def,
                       "AHU.AEW",
                       &value);
          len = sizeof (str) - 1;
          asn1_read_value (cert, name3, str, &len);
          asn1_der_decoding (&value, str, len, errorDescription);
          len = sizeof (str) - 1;
          asn1_read_value (value, "", str, &len);   /* CHOICE */
          strcpy (name3, str);
          len = sizeof (str) - 1;
          asn1_read_value (value, name3, str, &len);
          str[len] = 0;
          strcat (answer, " C=");
          strcat (answer, str);
          asn1_delete_structure (&value);
        }
          else
        {
          len = sizeof (str2) - 1;
          result =
            asn1_read_value (cert_def,
                     "AHU.ADK",
                     str2, &len);
          if (!strcmp (str, str2))
            {
              asn1_create_element (cert_def,
                       "AHU.AEW",
                       &value);
              len = sizeof (str) - 1;
              asn1_read_value (cert, name3, str, &len);
              asn1_der_decoding (&value, str, len, errorDescription);
              len = sizeof (str) - 1;
              asn1_read_value (value, "", str, &len);   /* CHOICE */
              strcpy (name3, str);
              len = sizeof (str) - 1;
              asn1_read_value (value, name3, str, &len);
              str[len] = 0;
              strcat (answer, " O=");
              strcat (answer, str);
              asn1_delete_structure (&value);
            }
          else
            {
              len = sizeof (str2) - 1;
              result =
            asn1_read_value (cert_def,
                     "AHU.ABF",
                     str2, &len);
              if (!strcmp (str, str2))
            {
              asn1_create_element (cert_def,
                           "AHU.ABU",
                           &value);
              len = sizeof (str) - 1;
              asn1_read_value (cert, name3, str, &len);
              asn1_der_decoding (&value, str, len,
                         errorDescription);
              len = sizeof (str) - 1;
              asn1_read_value (value, "", str, &len);   /* CHOICE */
              strcpy (name3, str);
              len = sizeof (str) - 1;
              asn1_read_value (value, name3, str, &len);
              str[len] = 0;
              strcat (answer, " OU=");
              strcat (answer, str);
              asn1_delete_structure (&value);
            }
            }
        }
        }
      k2++;
    }
      while (1);
      k++;
    }
  while (1);
}

/******************************************************/
/* Function : get_certificate                         */
/* Description: creates a certificate named           */
/*              "certificate2" from a der encoding    */
/*              string                                */
/* Parameters:                                        */
/*   unsigned char *der: the encoding string          */
/*   int der_len: number of bytes of der string      */
/******************************************************/
static void
get_certificate (ASN1_TYPE cert_def, unsigned char *der, int der_len)
{
  int result, len, start, end;
  unsigned char str[1024], str2[1024];
  ASN1_TYPE cert2 = ASN1_TYPE_EMPTY;
  char errorDescription[ASN1_MAX_ERROR_DESCRIPTION_SIZE];

  asn1_create_element (cert_def, "AHU.ALK", &cert2);

  result = asn1_der_decoding (&cert2, der, der_len, errorDescription);

  if (result != ASN1_SUCCESS)
    {
      printf ("Problems with DER encoding\n");
      return;
    }


  /* issuer */
  get_Name_type (cert_def, cert2, "AIX.APA", str);
  printf ("certificate:\nissuer :%s\n", str);
  /* subject */
  get_Name_type (cert_def, cert2, "AIX.AOT", str);
  printf ("subject:%s\n", str);


  /* Verify sign */
  len = sizeof (str) - 1;
  result = asn1_read_value (cert2, "AFU.ANW", str, &len);

  len = sizeof (str2) - 1;
  result =
    asn1_read_value (cert_def, "AHU.AHG", str2,
             &len);
  if (!strcmp ((char *) str, (char *) str2))
    {               /* dsa-with-sha */

      result = asn1_der_decoding_startEnd (cert2, der, der_len,
                       "AIX", &start, &end);

      /* add the lines to calculate the sha on der[start]..der[end] */

      len = sizeof (str) - 1;
      result = asn1_read_value (cert2, "ANH", str, &len);

      /* compare the previous value to signature ( with issuer public key) */
    }

  /* Use the next 3 lines to visit the certificate */
  /*   printf("-----------------\n");
     asn1_visit_tree(cert2,"");
     printf("-----------------\n"); */


  /* Clear the "certificate2" structure */
  asn1_delete_structure (&cert2);
}

extern const ASN1_ARRAY_TYPE pkix_asn1_tab[];