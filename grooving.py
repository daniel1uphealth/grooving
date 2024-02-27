import re
import sys

re_str = re.compile(r'\s*""(".*")""\s*');
re_concat = re.compile(r'\s*(((""")?).*\2)\s*(\+|\n)')

def parse_string(src):
    m = re_str.fullmatch(src)

    if m:
        return m.group(1)
    else:
        return None

def parse_ref(src):
    return src

def parse_concat(src):
    parts = re.findall(src)

    if parts:


parsers = [parse_string, parse_ref]

def translate(file):
    for line in file.readlines():
        print("Parsing %s" % line)
        (res_type, res_subtype, dest, src) = line.strip().split(',')

        print("src=%s" % src)
        if src == '""':
            sys.stdout.write('%s,%s,%s,\n' % (res_type, res_subtype, dest))
        else:
            for parser in parsers:
                result = parser(src)

                if result:
                    sys.stdout.write('%s,%s,%s,%s\n' % (res_type, res_subtype, dest, result))
                    break


if __name__ == "__main__":
    if len(sys.argv) == 1:
        translate(sys.stdin)
    elif len(sys.argv) == 2:
        translate(open(sys.argv[1], "r"))
    else:
        print("Unexpected arguments")