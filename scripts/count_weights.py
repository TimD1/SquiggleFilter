
model_type = "hac"
model_file = f"/home/timdunn/software/guppy_4_2_2/data/template_r9.4.1_450bps_{model_type}.jsn"

with open(model_file, 'r') as model:
    model_str = model.read()
    print(model_str.count("."))
