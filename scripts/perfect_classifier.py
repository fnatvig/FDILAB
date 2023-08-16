def filter(model, data):
    if data.iloc[0]["label"] == "attack":
        return "attack"
    else: 
        return "no_attack"