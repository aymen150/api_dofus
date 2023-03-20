
from PIL import Image
import models.detection.predict as predict
import models.classification.predict as predict_classification
from fastapi import File, UploadFile, FastAPI
import io
#pip install "uvicorn[standard]"
#pip install fastapi
# uvicorn server:app --reload

model_fight_en_cours =  "models/classification/in_fight/model.pb"
label_fight_en_cours = "models/classification/in_fight/labels.txt"

model = "models/detection/model_all_i12/model.pb"
label = "models/detection/model_all_i12/labels.txt"

model_fight = "models/detection/model_fight_i7/model.pb"
label_fight = "models/detection/model_fight_i7/labels.txt"

model_onglet = "models/detection/onglet_ressource_i3/model.pb"
label_onglet = "models/detection/onglet_ressource_i3/labels.txt"
od_model_ressource = predict.load_model(MODEL_FILENAME = model, LABELS_FILENAME = label)
od_model_fight = predict.load_model(MODEL_FILENAME = model_fight,LABELS_FILENAME = label_fight)
od_model_onglet = predict.load_model(MODEL_FILENAME = model_onglet,LABELS_FILENAME = label_onglet)
od_model_fight_en_cours = predict_classification.load_model(MODEL_FILENAME = model_fight_en_cours, LABELS_FILENAME = label_fight_en_cours)

app = FastAPI()

@app.get("/")
async def get_lol():
    return "hello world"

@app.get("/ressource")
async def get_ressource(file: bytes = File(...)):
        pil_image =  Image.open(io.BytesIO(file))
        predictions = od_model_ressource.predict_image(pil_image)
        return predictions

@app.get("/fight")
async def get_fight(file: bytes = File(...)):
        pil_image =  Image.open(io.BytesIO(file))
        predictions = od_model_fight.predict_image(pil_image)
        return predictions

@app.get("/fight/en_cours")
async def get_fight(file: bytes = File(...)):
        pil_image =  Image.open(io.BytesIO(file))
        classification = od_model_fight_en_cours.predict_image(pil_image)
        return classification

@app.get("/consommable")
async def get_consommable(file: bytes = File(...)):
        pil_image =  Image.open(io.BytesIO(file))
        predictions = od_model_onglet.predict_image(pil_image)
        return len( [x for x in predictions if (x["probability"] > 0.6)])
   