from dotenv import dotenv_values
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

config = dotenv_values(".env")
GOOGLE_API_KEY = config.get("GEMINI_API_KEY")
print(f"GOOGLE_API_KEY= {GOOGLE_API_KEY}")


# --- Define response data structure
class JadContent(BaseModel):
    """JAD type document content mapped to jad_content table"""

    # id: Mapped[int] = mapped_column(primary_key=True)
    # agreement_id: Mapped[int] = mapped_column(ForeignKey("agreement.id"), index=True)
    gerencia_solicitante: str = Field(
        description="text in 'Gerencia Solicitante' field"
    )
    rut_proveedor: str = Field(
        description="rut identifier text in 'Rut Proveedor' field"
    )
    nombre_proveedor: str = Field(
        description="proveedor name text in 'Razón Social Proveedor' field"
    )
    monto_uf: str = Field(description="text in 'Monto en UF' field")
    monto_uf_number: float = Field(description="amount in 'Monto en UF' field")
    cuenta_contable: str = Field(description="text in 'Cuenta Contable' field")
    centro_costo: str = Field(description="text in 'Centro de Costo' field")
    orden_controlling: str = Field(description="text in 'Orden Controlling' field")


# --- Convert image file to base64
image_path = "client_secret/753_response.pdf"
with open(image_path, "rb") as file:
    raw_binary = file.read()
    base64_bytes = base64.b64encode(raw_binary)  # type= bytes
    image_b64 = base64_bytes.decode(
        "utf-8"
    )  # type= str (neeeded for LLM message content)

# --- Initialize the model
model = init_chat_model(
    "gemini-2.5-flash", model_provider="google_genai", api_key=GOOGLE_API_KEY
)
structured_model = model.with_structured_output(JadContent)
system_prompt = """
ROLE: You are an expert Corporate Procurement Auditor and Multi-Modal Document Intelligence Agent. Your primary task is to visually analyze a document first page and extract form field data and return it in the JSON structured format provided by the user.

EXECUTION RULE: VISUAL-FIRST PROCESSING
1. Completely ignore any embedded, selectable PDF text layer string code, as its reading order may be corrupted.
2. Treat each page as a unified visual canvas.
3. Track multi-column fields, tables, and isolated text boxes spatially (Top-to-Bottom, Left-to-Right) based entirely on human reading logic.
4. Verify checkbox states (checked vs. unchecked) and the presence of physical or digital signatures visually. Do not hallucinate approvals.

## EXTRACTION OBJECTIVES
Analyze the form layout in the first part of the first page and extract the following data points into the provided structured schema. If a field is blank or physically missing populate it explicitly as "MISSING", if it is unreadable populate it explicitly as "UNREADABLE". If you find more than one value in the 'Cuenta Contable', 'Centro de Costo' or 'Orden Controlling' fields and are not already separated by a comma, then include a comma in the output string to separate these values.

## REQUESTED INFORMATION DATA POINTS:
1. 'Gerencia Solicitante' (requesting area) into 'gerencia_solicitante' key value.
2. 'Rut Proveedor' (Vendor Tax Id) into 'rut_proveedor' key value.
3. 'Razón Social Proveedor' (Vendor name) into 'nombre_proveedor' key value.
4. 'Monto en UF' (Amount plus text in UF currency) actual text in this field including letters and symbols into 'monto_uf' key value.
5. 'Monto en UF' (Only the amount in UF currency) only the amount in the field converted to float number. 90% of the times the amount uses '.' as thousand separator and ',' as decimal separator. If you find an amount with only two digits to the right of the '.' treat this '.' as a decimal separator instead of a thousand separator.
6. 'Cuenta Contable' (accounting account) into 'cuenta_contable' key value.
7. 'Centro de Costo' (cost center) into 'centro_costo' key value.
8. 'Orden Controlling' (controlling order number) into 'orden_controlling' key value.

# OUTPUT FORMAT
You must output your analysis in the user's provided JSON schema.
"""

# --- Create message
message = [
    {"role": "system", "content": system_prompt},
    {
        "role": "user",
        "content": "I have spinach leaves, eggs, onions, garlic, olive oil, butter, Monterey Jack cheese, and flour",
    },
]

# --- Get and print response
response = structured_model.invoke(message)
# Plain response
print(response)
print("- - -")
# Dictionary format response
response_dict = response.model_dump()
print(response_dict)
print("- - -")
