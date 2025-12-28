import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.get("/")
@app.get("/home")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)