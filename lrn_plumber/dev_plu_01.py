import time
from dotenv import dotenv_values
import pdfplumber

# STORAGE CONFIG
FOLDER_IN = "storage/jad/"
FOLDER_OUT = "storage/plumber_out/" 

#.ENV CONFIG
config = dotenv_values(".env")

def calc_exec_time(ts,te):
    execution_time = te - ts
    print(f"Execution time: {execution_time:.4f} seconds")

def extract_plumber():
      for i in range (1,2):
        print (f"---- {i} START ----")
        start_time = time.time()

        # FETCH FILE NAME from ".env"
        TST_FILE_NAME = config.get(f"TST_FILE_0{i}")
        print (f"{TST_FILE_NAME!r}")
    
        with pdfplumber.open(f"{FOLDER_IN}{TST_FILE_NAME}.pdf") as pdf:
            for n in range (0,4):
                page = pdf.pages[n]
                print(page.chars[n])
                print (f"---- PAGE {n} END ----- ")


        end_time = time.time()
        calc_exec_time(start_time,end_time)


def main():
    start_time = time.time()
    
    # FUNCTION TO RUN
    extract_plumber()

    end_time = time.time()
    calc_exec_time(start_time,end_time)
    print ("- - END - - ")
    return 0


if __name__ == "__main__":
    exit_code: int = main()
    print (f"exit code: {exit_code}")
    exit(exit_code)
