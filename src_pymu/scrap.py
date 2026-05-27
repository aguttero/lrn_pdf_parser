# from dotenv import dotenv_values

#.ENV CONFIG
# config = dotenv_values(".env")
# test_list = config.get("TEST_LIST")


with open("storage/jad6_fnames.txt", "r") as file:
    agreement_list = [line.strip() for line in file]

#print(f"agreement_list= {agreement_list!r}")
print(f"agreement_list= {agreement_list}")

