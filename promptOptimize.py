import json
def optimize(JPprompt:str):
    with open("optimizer.json","r") as f:
        try:
            rep_pr:dict = json.load(f)
            for i in rep_pr:
                JPprompt = JPprompt.replace(i,rep_pr[i])
            return JPprompt
        except Exception as e:
            print(e)
            return JPprompt