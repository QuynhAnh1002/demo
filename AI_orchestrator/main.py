from fastapi import FastAPI
import models.gemini_model
import models.gpt_model
import models.groq_model

app = FastAPI()

@app.get('/metadata')
async def getMetadata():
    pass

@app.post('/ask')
async def askQuestion():
    pass

@app.get('/status')
async def getStatus():
    pass