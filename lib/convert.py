#!/usr/bin/env python
import re

patterns = {
    '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
    '[đ]': 'd',
    '[èéẻẽẹêềếểễệ]': 'e',
    '[ìíỉĩị]': 'i',
    '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
    '[ùúủũụưừứửữự]': 'u',
    '[ỳýỷỹỵ]': 'y'
}


def unicode_to_ascii(text):
    """
    This function convert Unicode (Vietnamese) string to ASCII string
    Input: string to be converted
    Return: converted string
    """
    output = text
    for regex, replace in patterns.items():
        output = re.sub(regex, replace, output)
        # deal with upper case
        output = re.sub(regex.upper(), replace.upper(), output)
    return output


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        print(unicode_to_ascii(argv[1]))
    else:
        pass
