from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import models, transforms

app = FastAPI()

# Enable CORS to allow requests from any origin (or restrict to your front-end's URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up device and load the trained model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Load ConvNeXt-Tiny architecture
model = models.convnext_tiny(pretrained=False)
num_features = model.classifier[2].in_features
model.classifier[2] = torch.nn.Linear(num_features, 2)
# Load saved weights (make sure "best_model.pth" is in the same directory)
model.load_state_dict(torch.load("best_model.pth", map_location=device))
model = model.to(device)
model.eval()

# Define preprocessing (must match training)
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image_tensor = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            outputs = model(image_tensor)
            probs = F.softmax(outputs, dim=1).cpu().numpy()[0]
        pred_class = int(np.argmax(probs))
        label = "Real" if pred_class == 1 else "AI-Generated"
        confidence = float(probs[pred_class])
        return {"prediction": label, "confidence": confidence}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
