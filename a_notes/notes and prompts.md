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

