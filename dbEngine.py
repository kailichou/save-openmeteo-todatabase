from sqlalchemy import create_engine 
import json 


with open("config.json","r") as conf:
    conff = json.load(conf)
    db = conff["db"]

def start_engine(database=""):
    return create_engine("{}://{}:{}@{}:{}/{}".format(
        db["backend"],db["user"],db["password"],db["host"],db["port"],database)
    ) 


if __name__ == "__main__":
    try:
        # get the conn obj for the database
        engine = start_engine()
        print(
            f"Connection created successfully.")
    except Exception as ex:
        print("Connection could not be made due to the following error: \n", ex)