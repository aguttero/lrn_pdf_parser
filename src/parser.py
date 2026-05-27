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
    # file_handler.setLevel(logging.ERROR)
    # file_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # SET GLOBAL Config
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s",
        handlers=[console_handler, file_handler],
    )

    # CREATE LOGGER OBJECT
    global logger
    logger = logging.getLogger(__name__)
    ## LOGGER CONFIG END


# STORAGE CONFIG
FOLDER_IN = "storage/jad_pdf/"
FOLDER_OUT = "storage/jad_txt/"

# .ENV CONFIG
config = dotenv_values(".env")


def print_timestamp():
    from datetime import datetime

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(ts)
    return ts


def convert_pdf_to_words(file_name: str) -> list:
    """Converts file_name PDF content into a list of words
    Returns: list of words"""
    all_words_list = []
    with pymupdf.open(file_name) as doc:  # open a document
        logger.debug(f"found file name: {file_name!r}")
        for page in doc:  # iterate the document pages
            full_words = page.get_text("words")  # convert page into word tuples
            # PARSE WORDS:
            for word_tuple in full_words:
                all_words_list.append(word_tuple[4])
    # print(all_words_list)
    return all_words_list


def find_anchor_claude(tokens: list, *anchor_words) -> int:
    """Find the index of the first token in a known sequence of anchor words.
    Returns: int: -1 if the anchor word, or anchor word sequence does not exist in the given token list"""
    for i in range(len(tokens) - len(anchor_words) + 1):
        if all(
            tokens[i + j].lower() == anchor_words[j].lower()
            for j in range(len(anchor_words))
        ):
            return i
    return -1


def find_anchor(tokens: list, *anchor_words) -> int:
    """Find the index of the first token in a known sequence of anchor words.
    Returns: int: -1 if the anchor word, or anchor word sequence does not exist in the given token list"""
    total_tokens = len(tokens)
    total_anchors = len(anchor_words)
    search_limit = total_tokens - total_anchors + 1
    logger.debug(
        f"total_tokens len= {total_tokens}, total_anchors len= {total_anchors}, type(anchor_words)= {type(anchor_words)}"
    )

    for i in range(search_limit):
        anchor_match = True

        # Word by word comparison:
        for j in range(total_anchors):
            token_word = tokens[i + j].lower()
            anchor_word = anchor_words[j].lower()

            # if a single word does not match -> break loop
            if token_word != anchor_word:
                anchor_match = False
                break

        # If internal anchor loop finished and everything matched -> index found
        if anchor_match:
            logger.debug(
                f"Match found for anchor= {anchor_words} - Returning index= {i} "
            )
            return i
    # If we parsed al text and no complete coincidence:
    return -1  #  '-1' flag means: anchor words not found


def extract_until_anchor_claude(tokens, start, *stop_anchors):
    """Collect tokens from `start` until we hit any known stop anchor."""
    stop_sequences = [
        s.lower() if isinstance(s, str) else [x.lower() for x in s]
        for s in stop_anchors
    ]
    result = []
    i = start
    while i < len(tokens):
        # Check if current position matches any stop sequence
        for stop in stop_sequences:
            words = [stop] if isinstance(stop, str) else stop
            if tokens[i : i + len(words)] and all(
                tokens[i + j].lower() == words[j] for j in range(len(words))
            ):
                return result, i
        result.append(tokens[i])
        i += 1
    return result, i


def extract_until_anchor_gemini(tokens: list, start: int, stop_anchors: list) -> tuple:
    """
    Recolecta tokens desde 'start' hasta que encuentra cualquier secuencia de parada.
    Devuelve la lista de tokens recolectados y el índice donde se detuvo.
    """
    # 1. NORMALIZACIÓN: Convertimos todo a listas de palabras en minúsculas.
    # Si nos pasan ['fin'] se queda igual. Si nos pasan ['en', 'resumen'], también.
    secuencias_parada = []
    for secuencia in stop_anchors:
        secuencia_limpia = []
        for palabra in secuencia:
            secuencia_limpia.append(palabra.lower())
        secuencias_parada.append(secuencia_limpia)

    resultado = []
    i = start
    total_tokens = len(tokens)

    # 2. BUCLE PRINCIPAL: Recorremos el texto
    while i < total_tokens:
        # 3. VERIFICACIÓN: ¿Estamos parados sobre una secuencia de parada?
        detectado_stop = False

        for stop in secuencias_parada:
            largo_stop = len(stop)

            # Extraemos el fragmento del texto del mismo tamaño que la parada
            fragmento_texto = tokens[i : i + largo_stop]
            # Lo convertimos a minúsculas para comparar
            fragmento_minusculas = [palabra.lower() for palabra in fragmento_texto]

            # Si el fragmento coincide exactamente con la secuencia de parada
            if fragmento_minusculas == stop:
                detectado_stop = True
                break  # Rompe el bucle de las paradas

        # Si detectamos una parada, terminamos la función inmediatamente
        if detectado_stop:
            return resultado, i

        # Si no es una parada, guardamos la palabra y avanzamos
        resultado.append(tokens[i])
        i += 1

    # Si llegamos al final del texto sin encontrar ninguna parada
    return resultado, i


def parse_jad(tokens: list) -> dict:
    """Extracts data from a JAD token list
    Returns: dictionary"""
    result = {}

    # --- Date ---
    # Anchor: "Fecha:" → next token is the date
    idx = find_anchor(tokens, "Fecha:")
    if idx != -1:
        result["fecha"] = tokens[idx + 1]

    # --- Requesting area (Gerencia Solicitante) ---
    # Anchor: "Gerencia", "Solicitante" → collect until "Rut" anchor
    idx = find_anchor(tokens, "Gerencia", "Solicitante")
    if idx != -1:
        area_tokens, _ = extract_until_anchor_claude(
            tokens, idx + 2, ["Rut", "Proveedor"]
        )
        result["gerencia_solicitante"] = " ".join(area_tokens)
        logger.debug(f"area_tokens= {area_tokens!r}")

    # --- RUT Proveedor ---
    # Anchor/header: "Rut", "Proveedor", "Razón", "Social", "Proveedor", "SI/NO"
    # Anchor/header v2: "Social", "Proveedor", "SI/NO"
    # The RUT is the token immediately after this header block
    idx = find_anchor(tokens, "Social", "Proveedor", "SI/NO")
    if idx != -1:
        # Skip the full header: "Rut Proveedor Razón Social Proveedor SI/NO" (6 tokens)
        # Skip the full header v2: "Social Proveedor SI/NO" (3 tokens)
        header_end = idx + 3  # adjust if your header varies
        result["rut"] = tokens[header_end]

    # --- Razón Social Proveedor(Company Name) ---
    # Company name starts right after the RUT value, ends at next anchor
    if "rut" in result:
        rut_idx = tokens.index(result["rut"])
        name_tokens, _ = extract_until_anchor_claude(
            tokens, rut_idx + 1, ["Proveedor", "Relacionado"]
        )
        result["razon_social_proveedor"] = " ".join(name_tokens)
        logger.debug(f"name_tokens= {name_tokens!r}")

    # --- Monto en UF (UF Amount) ---
    # Anchor/header: 'Criticidad', 'del', 'Servicio'
    # The UF amount is the token immediately after this header block
    idx = find_anchor(tokens, "Criticidad", "del", "Servicio")
    if idx != -1:
        # Skip the full header: 'Criticidad', 'del', 'Servicio' (3 tokens)
        header_end = idx + 3  # adjust if your header varies
        uf_amount_float = float(
            tokens[header_end].strip().replace(".", "").replace(",", ".")
        )
        result["monto_uf"] = uf_amount_float
        logger.debug(f"monto_uf= {result['monto_uf']!r}")

    # --- Cuenta Contable (Accounting Account) ---
    # Anchor/header: 'Cuenta', 'Contable', 'Centro', 'de', 'Costo', 'Orden', 'Controlling'
    # Anchor/header v2: 'Costo', 'Orden', 'Controlling'
    # The account_id is the token immediately after this header block. 1 token in lenght
    idx = find_anchor(tokens, "Costo", "Orden", "Controlling")
    if idx != -1:
        # Skip the full header v2: 'Costo', 'Orden', 'Controlling' (3 tokens)
        cta_contable_idx = idx + 3  # adjust if your header varies
        result["cuenta_contable"] = tokens[cta_contable_idx]
        logger.debug(f"cuenta_contable= {result['cuenta_contable']!r}")

    # --- Centro de Costo (Cost Center) ---
    # Cost Center starts right after the 'Accounting Account' value, 1 token in lenght
    if "cuenta_contable" in result:
        centro_costo_idx = cta_contable_idx + 1
        result["centro_costo"] = tokens[centro_costo_idx]
        logger.debug(f"centro_costo= {result['centro_costo']!r}")

    # --- Orden Controlling (Controlling Order) ---
    # Orden Controlling starts right after the 'Cost Center' value, 1 token in lenght
    if "centro_costo" in result:
        orden_ctrl_idx = centro_costo_idx + 1
        result["order_controlling"] = tokens[orden_ctrl_idx]
        logger.debug(f"order_controlling= {result['order_controlling']!r}")

    # --- SENDER  ---
    # Sender is the first email after the agreemen id token

    return result


def save_words_file(words_list: list, pdf_filename: str):
    """Saves input list to TXT file in FOLDER_OUT directory. Renames the file from .pdf to .txt"""
    file_name_wo_ext = pdf_filename.rsplit(".")[0]

    with open(f"{file_name_wo_ext}.txt", "w") as file:
        file.write(f"{words_list}")


def main():
    init_logger()
    start_time = time.time()
    logger.debug(f"MAIN START - start time= {start_time}")
    # file_name = config.get("TST_FILE_01")

    # STEP 1 - FETCH AGREEMENT LIST FROM FILE
    with open("storage/jad6_fnames.txt", "r") as file:
        agreement_list = [line.strip() for line in file]

    logger.debug(
        f"agreement_list_len= {len(agreement_list)} agreement_list= {agreement_list!r} "
    )

    # STEP 1 - FETCH AND CONVERT PDF FILE TO WORD LIST
    # for i in range (1,2):
    for agrmnt in agreement_list:
        # TEST CODE FETCH FILE NAME from ".env"
        # file_name = config.get(f"TST_FILE_0{i}")

        file_name_pdf = f"{agrmnt}.pdf"
        logger.debug(f"Fetching file= {file_name_pdf!r}")

        # CONVERT FILE TO WORD LIST
        word_list = convert_pdf_to_words(f"{FOLDER_IN}{file_name_pdf}")
        # print (word_list)

        # SAVE TO OUTPUT FOLDER
        save_words_file(word_list, f"{FOLDER_OUT}{file_name_pdf}")

    # STEP 2 - PARSE WORD LIST
    # GET TOKENS
    # tokens = word_list

    # data = parse_jad(tokens)
    # logger.debug(f"data type= {type(data)}, data= {data}")

    end_time = time.time()
    exec_time = end_time - start_time
    logger.info(f"MAIN END - exec_time= {exec_time:.4f} seconds, end_time= {end_time}")
    print("- - END - - ")
    return 0


if __name__ == "__main__":
    exit_code: int = main()
    print(f"exit code: {exit_code}")
    exit(exit_code)
