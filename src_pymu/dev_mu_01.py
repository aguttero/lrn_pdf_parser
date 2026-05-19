import time
import pymupdf
from dotenv import dotenv_values
# import pymupdf4llm, json

# STORAGE CONFIG
FOLDER_IN = "storage/jad/"
FOLDER_OUT = "storage/test_out/" 

#.ENV CONFIG
config = dotenv_values(".env")

def print_timestamp():
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print (ts)
    return ts

def calc_exec_time(ts,te):
    execution_time = te - ts
    print(f"Execution time: {execution_time:.4f} seconds")

def convert_txt():
    for i in range (1,5):
        print (f"---- {i} START ----")
        start_time = time.time()

        # FETCH FILE NAME from ".env"
        TST_FILE_NAME = config.get(f"TST_FILE_0{i}")
        print (f"{TST_FILE_NAME!r}")

        # CONVERT TO TXT
        doc = pymupdf.open(f"{FOLDER_IN}{TST_FILE_NAME}.pdf") # open a document
        out = open(f"{FOLDER_OUT}{TST_FILE_NAME}.txt", "wb") # create a text output
        for page in doc: # iterate the document pages
            text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
            out.write(text) # write text of page
            out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
        out.close()
        end_time = time.time()
        calc_exec_time(start_time,end_time)
    print ("--- LOOP END ---")

def main():
    start_time = time.time()

    convert_txt()

    end_time = time.time()
    calc_exec_time(start_time,end_time)
    print ("- - END - - ")
    return 0


if __name__ == "__main__":
    exit_code: int = main()
    print (f"exit code: {exit_code}")
    exit(exit_code)


