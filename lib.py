import os
import ctypes


def debitcredit(input):
    """Return C if input is > 0 else D
        Used for bank statement parsing, thus, c and d as seen from the perspective of the bank's accountant"""
    return "C" if input >= 0 else "D"


def tatextcleaner(string):
    """"Cleaner function, add desc"""

    temp = string
    if(True):  # cleaned, removes iban, bic and uci
        if("IBAN" in string and "BIC" in string):
            temp = string[:string.index("IBAN")]
            temp += "    ||    "
            if("UCI" in string):
                temp += string[string.index(" ", string.find("BIC: ") + len("BIC: ")): string.find("UCI: ")]
            else:
                try:
                    temp += string[string.index(" ", string.find("BIC: ") + len("BIC: ")):]
                except ValueError:
                    pass

    if(False):  # traditional way
        pos = string.find("BIC: ")  # string that should be in every regular description
        if pos != -1:  # there was one entry where it was missing
            temp = string.insert(spacer, string.index(" ", pos + len("BIC: "))).insert(spacer, tatext.index("UCI: "))
    return temp


def createOutputFile(path):
    """Create file, overwrite existing"""

    try:
        output_file = open(path, 'x')  # create output file
    except OSError:  # as error:  # if already exists, remove and overwrite
        try:
            os.remove(path)
        except PermissionError:
            ctypes.windll.user32.MessageBoxW(0, f"Close output file {path}!\nCan't write data if file is open.", "Warning", 0 | 0x30)
            # print(f"\033[1;31;40m Close {path}!")
            quit()
    else:
        output_file.close()


def openOutputFile(path, *args, **kwargs):
    """For output files: Check if file is opened by another application and if so show popup, else open file as usual"""

    if not isOutputFileClosed(path):
        quit()
    else:
        return open(path, *args, **kwargs)


def isOutputFileClosed(path):
    """Returns true if target output file is closed, else false.
        Shows popup if file already in use.
        Clears contents, so only usable for mode 'w'"""
    try:
        f = open(path, "w")
        f.close()
        return True
    except PermissionError:
        ctypes.windll.user32.MessageBoxW(0, f"Close output file {path}!\nCan't write data if file is open.", "Warning", 0 | 0x30)
        # print(f"\033[1;31;40m Close {path}!")
        return False
