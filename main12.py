from fastapi import FastAPI, Form, Request, Depends, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
from datetime import datetime
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database.db_conn import DatabaseManager
from app.core.logger import Logger
from app.core.config import Config
import json
from fastapi.templating import Jinja2Templates

config = Config()
run_id = config.get_run_id()
logger = Logger()
dic={}

# Initialize FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# A simple in-memory database (just for the example, you can use a real database)
users_db = {}

# Basic login credentials for testing
admin_credentials = {"admin": "password"}

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust if necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allows all method
    allow_headers=["*"],  # Allows all headers
)

# Load model and scaler
model_path = 'app/model/house_price_model.pkl'
scaler_path = 'app/model/scaler.pkl'

with open(model_path, 'rb') as model_file, open(scaler_path, 'rb') as scaler_file:
    model = pickle.load(model_file)
    scaler = pickle.load(scaler_file)

# Pydantic model for input validation
class InputData(BaseModel):
    square_footage: int
    num_bedrooms: int
    num_bathrooms: int
    lot_size: float
    garage_size: int
    neighborhood_quality: int
    age: int  # Age is included directly in the input data


# Static files setup (if you have static files like CSS/JS)
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Route to serve login page
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# # Route for rendering the HTML page
# @app.get("/", response_class=HTMLResponse)
# async def index():
#     with open("app/templates/index.html") as f:
#         return f.read()


# Route to handle login
@app.post("/login", response_class=HTMLResponse)
async def process_login(request: Request, username: str = Form(...), user_password: str = Form(...)):
    mydb = DatabaseManager() 
    
    
    try:
        mydb.connect()
        mydb.create_users_table()
        x = mydb.login_check(username,user_password)
        if x=='good':
            return templates.TemplateResponse("index.html", {"request": request, "username": username})
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    except Exception as e:
        print(e)
    finally:
        mydb.close_connection()


# Route to handle registration page
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Route to handle user registration
@app.post("/register", response_class=HTMLResponse)
async def process_registration(request: Request, username: str = Form(...), user_password: str = Form(...), confirm_password: str = Form(...)):
    if user_password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match"})
    mydb = DatabaseManager()   
    
    try:
        mydb.connect()
        mydb.create_users_table()
        x = mydb.login_check(username,user_password)
        if x=='good':
            return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})
        else:
            mydb.register_user(username,user_password)
    except Exception as e:
        print(e)
    finally:
        mydb.close_connection()       
    
    users_db[username] = user_password
    return templates.TemplateResponse("login.html", {"request": request, "message": "Registration successful! Please login."})


# Route for prediction
@app.post("/predict")
async def predict(data: InputData):
    mydb = DatabaseManager() 
    try:
        # Connect to database
        mydb.connect()
        logger.info({"connection": "Database connected successfully", "run_id": run_id})

        # Prepare and map input data to model's feature names
        input_data = {
            "Square_Footage": data.square_footage,
            "Num_Bedrooms": data.num_bedrooms,
            "Num_Bathrooms": data.num_bathrooms,
            "Lot_Size": data.lot_size,
            "Garage_Size": data.garage_size,
            "Neighborhood_Quality": data.neighborhood_quality,
            "Age": data.age,
        }
        logger.info({"input_data": input_data})

        # Create table
        mydb.create_table('predictions', r'app/database/schema_prediction.json')
        logger.info({"table_status": "Table created successfully"})

        # Insert input data into table
        mydb.insert_data('predictions', input_data)
        logger.info({"insert_status": "Data inserted successfully"})

        # Preprocess data
        input_df = pd.DataFrame([input_data])
        input_scaled = scaler.transform(input_df)

        # Make prediction
        prediction = model.predict(input_scaled)[0]
        logger.info({"prediction": prediction})

        # Return response
        return {"predicted_house_price": f"${prediction:,.2f}"}

    except Exception as e:
        logger.exception({"error": str(e)})
        return {"error": str(e)}

    finally:
        mydb.close_connection()
        logger.info({"connection is closed"})

# Run the FastAPI application
if __name__ == '__main12__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)