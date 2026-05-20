import time
from datetime import datetime
import pymupdf
from dotenv import dotenv_values


def init_logger():
    # LOGGER CONFIG START
    import logging

    # SET LEVEL for each Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    now = datetime.now()
    filestamp = now.strftime("%Y%m%d_%H_%M")

    file_handler = logging.FileHandler(f"logs/dev_{filestamp}.log")
    #file_handler.setLevel(logging.ERROR)
    #file_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # SET GLOBAL Config
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s',
        handlers=[console_handler,file_handler]
    )

    # CREATE LOGGER OBJECT
    global logger
    logger = logging.getLogger(__name__)
    ## LOGGER CONFIG END


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

def convert_pdf_to_words(file_name:str)-> list:
    """Converts file_name PDF content into a list of words
        Returns: list of words"""
    all_words_list = []
    with pymupdf.open(file_name) as doc: # open a document
         logger.debug(f"found file name: {file_name!r}")
         for page in doc: # iterate the document pages
            full_words = page.get_text("words") # convert page into word tuples 
            # PARSE WORDS:
            for word_tuple in full_words:
                all_words_list.append(word_tuple[4])
    #print(all_words_list)
    return all_words_list

def find_anchor(tokens:list, *anchor_words)->int:
    """Find the index of the first token in a known sequence of anchor words.
        Returns: int: -1 if the anchor word, or anchor word sequence does not exist in the given token list"""

    # ORIGINAL FUNCTION START
    # for i in range(len(tokens) - len(anchor_words) + 1): #limits loop to total list length - anchor list length + 1 to avoid searching out of the list (index out of range error)
    #     if all(tokens[i + j].lower() == anchor_words[j].lower() for j in range(len(anchor_words))):
    #         return i
    # return -1 #  '-1' flag means: anchor words not found
    # ORIGINAL FUNCITON END 

    # SAME FUNCTION EASIER TO READ START
    total_tokens = len(tokens)
    total_anchors = len(anchor_words)
    search_limit = total_tokens - total_anchors + 1
    logger.debug(f"total_tokens len= {total_tokens}, total_anchors len= {total_anchors}, type(anchor_words)= {type(anchor_words)}")
    
    for i in range (search_limit):
        anchor_match = True

        # Word by word comparison:
        for j in range (total_anchors):
            token_word = tokens[i + j].lower()
            anchor_word = anchor_words[j].lower()

            # if a single word does not match -> break loop
            if token_word != anchor_word:
                anchor_match = False
                break
        
        # If internal anchor loop finished and everything matched -> index found
        if anchor_match:
            logger.debug(f"Match found for anchor= {anchor_words} - Returning index= {i} ")
            return i
    # If we parsed al text and no complete coincidence:
    return -1 #  '-1' flag means: anchor words not found


def parse_jad(tokens:list)-> dict:
    """Extracts data from a JAD token list
        Returns: dictionary"""
    result_dict = {}

    # --- Date ---
    # Anchor: "Fecha:" → next token is the date
    idx = find_anchor(tokens, "Fecha:")
    if idx != -1:
        result_dict["fecha"] = tokens[idx + 1]

    return result_dict

def save_words_file(words_list:list, pdf_filename:str):
    """Saves input list to TXT file in FOLDER_OUT directory. Renames the file from .pdf to .txt """
    file_name_wo_ext = pdf_filename.rsplit('.')[0]

    with open (f"{file_name_wo_ext}.txt","w") as file:
        file.write(f"{words_list}")


def main():
    init_logger()
    start_time = time.time()
    logger.debug(f"MAIN START - start time= {start_time}")
    # file_name = config.get("TST_FILE_01")

    # STEP 1 - FETCH AND CONVERT PDF FILE TO WORD LIST
    #for i in range (1,5):
    for i in range (1,2):

        # FETCH FILE NAME from ".env"
        file_name = config.get(f"TST_FILE_0{i}")
        logger.debug(f"Fetched file name from .env: {file_name!r}")

        # CONVERT FILE TO WORD LIST
        word_list = convert_pdf_to_words(f"{FOLDER_IN}{file_name}")
        # print (word_list)

        # SAVE TO OUTPUT FOLDER
        # save_words_file(word_list, f"{FOLDER_OUT}{file_name}")

    # STEP 2 - PARSE WORD LIST
    # GET TOKENS
    tokens = word_list

    data = parse_jad(tokens)
    logger.debug(f"data type= {type(data)}, data= {data}")

    end_time = time.time()
    exec_time = end_time - start_time
    logger.info(f"MAIN END - exec_time= {exec_time:.4f} seconds, end_time= {end_time}")
    print ("- - END - - ")
    return 0


if __name__ == "__main__":
    exit_code: int = main()
    print (f"exit code: {exit_code}")
    exit(exit_code)


