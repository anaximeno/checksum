# Author: Anaximeno Brito
# Calculates the file sum and compares it with an given sum
# 2020

#%%
import argparse
from processing.process import Process
from processing.hashes import hashes


# get all types of sums
tp = ""
for item in hashes:
    tp += " " + item

#%%
# principal function
def main():
    parser = argparse.ArgumentParser(
        description="Check and Compare the sums.",
        usage="checksum [OPTION] content...",
        epilog="Author: Anaximeno Brito, <anaximenobrito@gmail.com>"
    )

    option = parser.add_mutually_exclusive_group()

    option.add_argument("-f", "--file",
                        help="Check the sum of one object (file) which have the name and sum wrote in the file.",
                        action="store_true")

    option.add_argument("-F", "--Files",
                        help="Check the sum of all objects (files) which have the name and sum wrote in the file.",
                        action="store_true")

    option.add_argument("-A", "--all", help="Print all the sums of one file",
                        action="store_true")

    option.add_argument("-v", "--version", help="Print the current version of this app.", action="store_true")

    parser.add_argument("content", help="file name or sum depending of the choice", nargs='?', default=None)

    parser.add_argument("--verbose", help="Verbose response", action="store_true")

    for s in hashes:
        option.add_argument(f"-{s}", f"--{s}sum", metavar='')  # metavar is empty

    args = parser.parse_args()


    def make_process(ac, st, fn):
        # ac is file sum, fn is file name, st is sum type
        if ac:
            prc = Process(file=fn, sumType=st, hashSum=ac)
            prc.normal()
            if args.verbose:
                prc.verbose()
        else:
            only_sum = input("Do you only want check the sum, without compare it? [Y/n]: ")
            if not only_sum or only_sum.isspace() or only_sum.lower() == "yes" or only_sum.lower == "y":
                prc = Process(file=fn, sumType=st)
                prc.only_sum()
            else:
                print("Aborted!")
                print("usage: checksum [SUMTYPE] file_NAME file_SUM")
                print("or: checksum -h, for more information.")

    prc = Process(file=args.content)

    if args.version:
        # must get of one txt file!!
        print("checksum 0.2.4")
    elif args.file:
        if args.content:
            prc.text()
        else:
            parser.error("expected one argument")
    elif args.Files:
        if args.content:
            prc.multi_files()
        else:
            parser.error("expected one argument")
    elif args.all:
        if args.content:
            prc.allsums()
        else:
            parser.error("expected one argument")
    elif args.md5sum:
        make_process(args.content, "md5", args.md5sum)
    elif args.sha1sum:
        make_process(args.content, "sha1", args.sha1sum)
    elif args.sha224sum:
        make_process(args.content, "sha224", args.sha224sum)
    elif args.sha256sum:
        make_process(args.content, "sha256", args.sha256sum)
    elif args.sha384sum:
        make_process(args.content, "sha384", args.sha384sum)
    elif args.sha512sum:
        make_process(args.content, "sha512", args.sha512sum)
    elif args.content:  # must be the penultimate
        want_all = input("Do you want to check all '{}' sums? [Y/n]: ".format(args.content))
        if not want_all or want_all.isspace() or want_all.lower() == "yes" or want_all.lower() == "y":
            print("")  # skip one line
            prc.allsums()
        else:
            print("Aborted!")
            print("usage: checksum [OPTION] content...")
            print("or: checksum -h, for more information.")
    else:
        parser.error("No options was chosen, try: checksum -h, for more information.")
