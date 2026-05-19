import time
import pymupdf
from dotenv import dotenv_values
import json

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

def convert_blocks():
    for i in range (1,2):
        print (f"---- {i} START ----")
        start_time = time.time()

        # FETCH FILE NAME from ".env"
        TST_FILE_NAME = config.get(f"TST_FILE_0{i}")
        print (f"{TST_FILE_NAME!r}")

        # CONVERT TO TXT BLOCKS
        doc = pymupdf.open(f"{FOLDER_IN}{TST_FILE_NAME}.pdf") # open a document
        # out = open(f"{FOLDER_OUT}{TST_FILE_NAME}.txt", "wb") # create a text output
        for page in doc: # iterate the document pages
            blocks = page.get_text("blocks") # get blocks text (is in UTF-8)
            
            # out.write(text) # write text of page
            # out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
            print (f"blocks={blocks}")
            print ("--- PRINT BLOKCS END ---")
            for block in blocks:
                print (f"block_item={block}")
                print ("--- BLOKC ITEM END ---")
            print ("---- PAGE END ----")
        print ("---- LOOP END ----")
        
        # out.close()


        end_time = time.time()
        calc_exec_time(start_time,end_time)

def convert_words():
    all_words = []
    for i in range (1,2):
        print (f"---- {i} START ----")
        start_time = time.time()

        # FETCH FILE NAME from ".env"
        TST_FILE_NAME = config.get(f"TST_FILE_0{i}")
        print (f"{TST_FILE_NAME!r}")

        # CONVERT TO TXT WORDS
        doc = pymupdf.open(f"{FOLDER_IN}{TST_FILE_NAME}.pdf") # open a document
        # out = open(f"{FOLDER_OUT}{TST_FILE_NAME}.txt", "wb") # create a text output
        for page in doc: # iterate the document pages
            words = page.get_text("words") # get blocks text (is in UTF-8)
            
            # out.write(text) # write text of page
            # out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
            print (f"words={words}")
            print ("--- PRINT BLOKCS END ---")
            for word in words:
                print (f"word_item={word}")
                all_words.append(word[4])
                print ("--- BLOKC ITEM END ---")
            print ("---- PAGE END ----")
        print ("---- LOOP END ----")
        print ("all_words:\n", all_words)

        # out.close()


        end_time = time.time()
        calc_exec_time(start_time,end_time)

def convert_json():
    for i in range (1,2):
        print (f"---- {i} START ----")
        start_time = time.time()

        # FETCH FILE NAME from ".env"
        TST_FILE_NAME = config.get(f"TST_FILE_0{i}")
        print (f"{TST_FILE_NAME!r}")

        # CONVERT TO TXT WORDS
        doc = pymupdf.open(f"{FOLDER_IN}{TST_FILE_NAME}.pdf") # open a document
        # out = open(f"{FOLDER_OUT}{TST_FILE_NAME}.txt", "wb") # create a text output
        for page in doc: # iterate the document pages
            json_string = page.get_text("json") # get blocks text (is in UTF-8)
            
            # out.write(text) # write text of page
            # out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
            
            page_data = json.loads(json_string)
            print("json:\n", json.dumps(page_data, indent=2))
            print ("--- JSON PAGE END ---")
            print ("---- PAGE END ----")
        print ("---- LOOP END ----")

        # out.close()
        end_time = time.time()
        calc_exec_time(start_time,end_time)


def main():
    start_time = time.time()

    # convert_txt()
    # convert_blocks()
    # convert_words()
    convert_json()


    end_time = time.time()
    calc_exec_time(start_time,end_time)
    print ("- - END - - ")
    return 0


if __name__ == "__main__":
    exit_code: int = main()
    print (f"exit code: {exit_code}")
    exit(exit_code)


