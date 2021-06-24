import csv
import datetime
import os
import tkinter
from tkinter.filedialog import askopenfilename
import german_normalize
from tqdm import tqdm


def insert(self, insert_str, pos):
    return self[:pos] + insert_str + self[pos:]


# debit and credit as seen from the perspective of a bank's accountant
def debitcredit(input): return "C" if input >= 0 else "D"


def tatextcleaner(string):
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


# --- file input and file name prep
tkinter.Tk().withdraw()
input_file_path = askopenfilename(initialdir='C:/Users/Markus/Downloads', title="Select file",
                                  filetypes=[("Text Files", "*.csv")])  # initialdir=os.getcwd()
if not input_file_path:
    print("\nCancelled file selection, terminating script")
    exit()
input_file_name = input_file_path.split("/")[-1]
# .sta presumably for '(bank) statement'
output_file_name = input_file_name.replace("csv", "sta")
output_file_path = '/'.join(input_file_path.split("/")
                            [:-1]) + '/' + output_file_name
metadata = input_file_name.split('-')

# --- prep meta data
# transactrefnum is in the format DDDHHMM where DDD is the number of days since Jan 1st
transactrefnum = str(datetime.date(int(metadata[0], 10), int(
    metadata[1], 10), int(metadata[2], 10)).timetuple().tm_yday) + metadata[3][:4]
print(transactrefnum)
iban = "/"  # "DE87 7002 2200 0020 1762 29"
datedense = metadata[0][2:] + metadata[1] + metadata[2]
startbalance = 0.00
closingbalance = startbalance
currency = "EUR"
finalopeningbalance = debitcredit(
    startbalance) + datedense + currency + "{:.2f}".format(startbalance).replace(".", ",")

# --- create output file, delete if already exists
try:
    output_file = open(output_file_path, 'x', encoding='ascii')
except OSError as error:  # raise exception if file exists already to avoid partially overwriting redundant file >> right now coded to overwrite existing file
    # print("ERROR! ",error)
    os.remove(output_file_path)
else:
    output_file.close()

# --- data parsing
finally:
    # open input and output files and feed input to reader object
    input_file = open(input_file_path, 'r', encoding='utf-8')
    reader = csv.reader(input_file, delimiter=';')
    output_file = open(output_file_path, 'w', encoding='ascii')

    # write header
    output_file.write(
        ":20:{}\n:25:{}\n:28C:1/1\n:60F:{}".format(transactrefnum, iban, finalopeningbalance))

    # write transaction block
    next(reader)  # skip the header
    for line in tqdm(reversed(list(reader))):

        idate = line[0]
        tempdate = line[0].split('.')
        # if(len(tempdate)==1): #filter out the header
        #    continue
        valuedate = tempdate[2][2:] + tempdate[1] + tempdate[0]
        bookingdate = tempdate[1] + tempdate[0]
        value = float(line[3].replace('.', '').replace(',', '.'))
        dc = debitcredit(value)
        curr = currency[2]
        amount = str(abs(value)).replace('.', ',')
        ntrf = "NTRF"
        output_file.write("\n:61:" + valuedate +
                          bookingdate + dc + curr + amount + ntrf)

        closingbalance += value

        tacode = 0
        tadesc = ""
        tatext = line[1]
        spacer = "--------------------"
        if value > 0:
            tacode = "051"
            tadesc = "Überweisungsgutschrift"
            tatext = tatextcleaner(tatext)
        elif line[1][0:11] == "Lastschrift":
            tacode = "005"
            tadesc = "Lastschrift"
            tatext = tatextcleaner(tatext)
        else:  # Might cause errors with recognizing the ue, so better handle it as the last possible option
            tacode = "020"
            tadesc = "Überweisungsauftrag"
            try:
                tatext = line[2][:line[2].index("IBAN") - 2] + "    ||    " + line[1]
            except ValueError:
                tatext = line[2] + "    ||    " + line[1]
        tanum = str(0)  # Fidor doesn't provide that information
        for x in range(len(tatext) - 1):
            if int(x) % 35 == 0:
                tatext.insert("?" + str(int(20 + x / 35)), x)
        out = german_normalize.normalize("\n:86:" + tacode + "?00" + tadesc + "?10" + tanum + tatext, heuristic_case=True)
        output_file.write(out)
        # print(line[0],tatext)

    # write footer
    finalclosingbalance = debitcredit(
        closingbalance) + datedense + currency + "{:.2f}".format(closingbalance).replace(".", ",")
    output_file.write("\n:62F:" + finalclosingbalance + "\n-")

    output_file.close()
    input_file.close()
    print("\nSUCCESS!")
    # os.startfile(output_file_path)

# Model all the values in different types of objects?
