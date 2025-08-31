# MIT License
#
# Copyright (c) 2021 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from datetime import timedelta


def pprint(variable, indent=0):
    content = pprint_content(variable, indent)
    print(content)


def pprint_content(variable, indent=0):
    if variable is None:
        return '\t' * indent + "None"
    if not variable:
        ## empty container
        return '\t' * indent + "Empty"

    ret_list = []
    if isinstance( variable, dict ):
        for key, value in variable.items():
            ret_list.append('\t' * indent + str(key) + ":")
            content = pprint_content( value, indent + 1 )
            ret_list.append(content)
    elif isinstance( variable, list ):
        # pylint: disable=C0200
        for i in range(0, len(variable)):
            value = variable[i]
            ret_list.append('\t' * indent + "[" + str(i) + "]:")
            content = pprint_content( value, indent + 1 )
            ret_list.append(content)
    else:
        ret_list.append('\t' * (indent + 1) + str(variable))
    return "\n".join(ret_list)


def print_timedelta( value: timedelta ):
    s = ""
    secs = value.seconds
    days = value.days
    if secs != 0 or days == 0:
        mm, _ = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        s = "%d:%02d" % (hh, mm)                                # pylint: disable=C0209
#         s = "%d:%02d:%02d" % (hh, mm, ss)
    if days:
        def plural(n):
            return n, abs(n) != 1 and "s" or ""
        if s != "":
            s = ("%d day%s, " % plural(days)) + s               # pylint: disable=C0209
        else:
            s = ("%d day%s" % plural(days)) + s                 # pylint: disable=C0209
#     micros = value.microseconds
#     if micros:
#         s = s + ".%06d" % micros
    return s
