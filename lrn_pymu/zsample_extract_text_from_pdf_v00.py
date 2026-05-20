#import pymupdf
from dotenv import dotenv_values
# import pymupdf4llm, json

# STORAGE CONFIG
FOLDER_IN = "storage/"
FOLDER_OUT = "storage/test_out/" 

#.ENV CONFIG
config = dotenv_values(".env")
TST_FILE_PATH_01 = config.get("TST_FILE_01")
print (TST_FILE_PATH_01)

# for i in range (4):
    # file_in = config.get(f"TST_FILE_0{i+1}")


# doc = pymupdf.open(f"{FOLDER_IN}/response with audit trail_v01.pdf") # open a document
# out = open(f"{FOLDER_OUT}/JAD_AT_OUTPUT_v01.txt", "wb") # create a text output
# for page in doc: # iterate the document pages
#     text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
#     out.write(text) # write text of page
#     out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
# out.close()




