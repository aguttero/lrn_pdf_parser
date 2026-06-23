# prompt for json parse
Plan python function to extract a list of dictionaries with the participant information contained in a list as value of key "participantSetsInfo"

The sample json response file from where to extract the data is in: `client_secret/sample_agr_info_test.json`

This is is the expected format for the extract function: one dictionary for each member in the "participantSetsInfo" list.

participant_list = [{
    "email": email_addres,
    "name": name,
    "role": role,
    "order": order,
    "label": label
}]

ask clarification questions if needed.

Once the plan is approved by me. Write the code in: `src/main.py`

# system prompt visual inspection and extraction
## ROLE
You are an expert Corporate Procurement Auditor and Multi-Modal Document Intelligence Agent. Your primary task is to visually analyze document images/pages to detect and audit policy-bypass requests (e.g., Sole Source / Single Source / Direct Purchase Order Authorization Forms).

## CRITICAL EXECUTION RULE: VISUAL-FIRST PROCESSING
1. Completely ignore any embedded, selectable PDF text layer string code, as its reading order may be corrupted.
2. Treat each page as a unified visual canvas.
3. Track multi-column fields, tables, and isolated text boxes spatially (Top-to-Bottom, Left-to-Right) based entirely on human reading logic.
4. Verify checkbox states (checked vs. unchecked) and the presence of physical or digital signatures visually. Do not hallucinate approvals.

## AUDIT AND EXTRACTION OBJECTIVES
Analyze the form layout and extract the following data points into a structured schema. If a field is blank, physically missing, or unreadable, mark it explicitly as "MISSING".

1. REQUEST DETAILS:
   - Requestor Name, Department, and Date.
   - Proposed Vendor Name.
   - Total Estimated Monetary Value (Look closely for currency symbols and handwritten/typed numbers).

2. PROCUREMENT BYPASS TRIGGER (Look for checked boxes or headers indicating the mechanism):
   - Type: [Sole Source / Emergency Procurement / Unique Technical Capability / OEM Monopoly / Other]

3. EXCEPTION JUSTIFICATION ANALYSIS:
   - Extract the raw text from the "Justification / Reason for Bypassing Competitive Bid" text block.
   - Assess Justification Strength: Rate as [STRONG / WEAK / INVALID]. 
   - Note: Generic phrases like "Vendor is the best," "Standard policy," or "Due to tight timelines" without concrete technical/emergency evidence must be flagged as WEAK or INVALID.

4. COMPLIANCE & SIGNATURE CHECK:
   - Identify all required signature blocks (e.g., Department Head, Procurement Director, CFO).
   - For each block, state: [SIGNATURE PRESENT (Physical/Digital) / BLANK / TYPED ONLY (No actual signature image)].

## OUTPUT FORMAT
You must output your analysis in valid, raw JSON format matching your designated extraction schema. Do not wrap the JSON in conversational filler or markdown text blocks other than the specified code block.

#  system prompt visual inspection and extraction with pydantic
## ROLE
You are an expert Corporate Procurement Auditor and Multi-Modal Document Intelligence Agent. Your primary task is to visually analyze document images/pages to detect and audit policy-bypass requests (e.g., Sole Source / Single Source / Direct Purchase Order Authorization Forms).

## CRITICAL EXECUTION RULE: VISUAL-FIRST PROCESSING
1. Completely ignore any embedded, selectable PDF text layer string code, as its reading order may be corrupted.
2. Treat each page as a unified visual canvas.
3. Track multi-column fields, tables, and isolated text boxes spatially (Top-to-Bottom, Left-to-Right) based entirely on human reading logic.
4. Verify checkbox states (checked vs. unchecked) and the presence of physical or digital signatures visually. Do not hallucinate approvals.

## SCHEMA MAPPING & EXTRACTION INSTRUCTIONS
You must populate the user's provided JSON schema according to these visual extraction rules:

1. COMPLIANCE & SIGNATURES:
   - Carefully look at the physical signature lines. 
   - Map them to the schema strictly as: "PRESENT" (if a handwritten/digital signature image exists), "BLANK" (if empty), or "TYPED_ONLY" (if just a typed name with no signature markup).

2. JUSTIFICATION STRENGTH:
   - Read the written justification text block. 
   - Evaluate its compliance strength based on context and map it strictly to the allowed enum values: "STRONG", "WEAK", or "INVALID". Generic excuses like "Tight deadlines" or "Vendor is standard" must be classified as "WEAK" or "INVALID".

3. EMPTY FIELDS:
   - If a text field in the form is physically blank, unreadable, or missing, populate it exactly as `null` (or an empty string `""` depending on schema restrictions). Do not invent data.

# GOOGLE GENAI SDK EXAMPLE
## Required PIP install
pip install google-genai
https://googleapis.github.io/python-genai/


## python code:
```python
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

# Read the raw binary data
with open("procurement_bypass_form.pdf", "rb") as f:
    pdf_bytes = f.read()

response = client.models.generate_content(
    model='gemini-2.5-pro',
    contents=[
        types.Part.from_bytes(
            data=pdf_bytes,
            mime_type='application/pdf',
        ),
        "Analyze this procurement exception form."
    ],
    config=types.GenerateContentConfig(
        system_instruction="...[Your System Prompt]...",
        response_mime_type="application/json",
        response_schema=ProcurementAuditSchema,
        temperature=0.0
    ),
)

print(response.text)
```
## Passing Pydantic Schema

To pass your Pydantic schema to Gemini using the native google-genai SDK, you provide your Pydantic class directly to the response_schema parameter inside GenerateContentConfig. Under the hood, Google’s SDK automatically extracts the fields, types, and descriptions to enforce a perfect JSON match.
Here is the exact production-ready pattern.
### 1. Define your Pydantic Class
Make sure to include Field(description="...") tags. Gemini relies heavily on these descriptions to know exactly what visual information on the form maps to which variable.

```python
from enum import Enumfrom typing import Optionalfrom pydantic import BaseModel, Field
# 1. Define Enums for rigid visual classificationclass SignatureState(str, Enum):
    PRESENT = "PRESENT"
    BLANK = "BLANK"
    TYPED_ONLY = "TYPED_ONLY"
class JustificationRating(str, Enum):
    STRONG = "STRONG"
    WEAK = "WEAK"
    INVALID = "INVALID"
# 2. Build the main layout extraction schemaclass ProcurementAuditSchema(BaseModel):
    requestor_name: Optional[str] = Field(
        description="Full name of the individual requesting the PO bypass. Return null if empty."
    )
    vendor_name: str = Field(
        description="The named vendor or supplier proposed on the form."
    )
    estimated_value: float = Field(
        description="The total monetary amount requested. Clean any currency symbols; extract purely the float value."
    )
    justification_text: str = Field(
        description="The exact text block describing why the standard bid process is being bypassed."
    )
    justification_strength: JustificationRating = Field(
        description="Classify the justification. Mark WEAK if it relies on timeline excuses alone."
    )
    manager_signature: SignatureState = Field(
        description="Look at the Manager approval block. Check if a real physical or digital signature is visible."
    )
    cfo_signature: SignatureState = Field(
        description="Look at the CFO signature line. Classify whether it contains a signature image or is blank."
    )
```
### 2. Pass the Schema to the Generation Config
When calling generate_content, you must specify both response_mime_type="application/json" and response_schema=YourClass.
```python
from google import genaifrom google.genai import types
# Initialize the native Google Gen AI Clientclient = genai.Client(api_key="YOUR_GEMINI_API_KEY")
# Upload the unstructured PDF form fileform_pdf = client.files.upload(file="chaotic_procurement_form.pdf")
# Execute the extractionresponse = client.models.generate_content(
    model='gemini-2.5-pro', # Use 'pro' models for dense visual forms and auditing
    contents=[
        form_pdf, 
        "Analyze the visual layout of this form and audit the procurement bypass request."
    ],
    config=types.GenerateContentConfig(
        system_instruction="You are a strict procurement auditor. Treat the PDF as a visual map.",
        # --- Crucial Parameters for Pydantic Matching ---
        response_mime_type="application/json",
        response_schema=ProcurementAuditSchema, 
        # ------------------------------------------------
        temperature=0.0 # Force deterministic output
    ),
)
```

### 3. Handle the Output
Google’s SDK returns a raw JSON string that perfectly matches your structure. You can load it directly back into Pydantic to get a fully validated Python object with auto-complete and type validation: [1, 2, 3] 
```python
import json
# Parse the raw JSON text string back into a Pydantic objectaudit_data = ProcurementAuditSchema.model_validate_json(response.text)
# Access fields natively with full Python type-safety
print(f"Vendor: {audit_data.vendor_name}")
print(f"Value: ${audit_data.estimated_value:,}")
print(f"Justification Strength: {audit_data.justification_strength.value}")
if audit_data.cfo_signature == SignatureState.BLANK:
    print("🚨 WARNING: Missing critical CFO signature!")
```

### Important Execution Notes

* Nested Structures: If your form has a table with itemized lines, Gemini supports nested structures natively. You can create a second class class LineItem(BaseModel): and include it in your main schema as items: list[LineItem].
* Model Choice: Use gemini-2.5-pro or gemini-1.5-pro. The smaller flash models frequently stumble when forced to map messy visual data into precise Pydantic schemas. [4] 

Do your forms contain complex multi-row tables or an unknown number of line items that we need to add to this Pydantic schema structure?

[1] [https://invoicedataextraction.com](https://invoicedataextraction.com/sdk/python)
[2] [https://agenta.ai](https://agenta.ai/docs/changelog/customize-llm-as-a-judge-output-schemas)
[3] [https://biocypher.org](https://biocypher.org/BioChatter/features/structured_outputs/)
[4] [https://medium.com](https://medium.com/@mohammed97ashraf/how-to-generate-structured-outputs-with-googles-gemini-api-a-comprehensive-guide-384421650e21)
