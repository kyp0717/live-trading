from flask import Flask, render_template
from dotenv import load_dotenv
import sys

# import benchmark as bm
from utils import benchmark as bm

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/kepl/work/live-trading/flaskapp/utils')

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.template_folder('public')

@app.route("/")
def home():
    return render_template("principal.html")
    # return render_template("principal.html")

@app.route("/market")
def market():
    spybm = bm.Benchmark('SPY', live=False)
    s = spybm.run().to_dict()
    # print(s)
    return render_template("market.html",spy=s)

@app.route("/sector")
def sector():
    return render_template("sector.html")

@app.route("/assets")
def assets():
    return render_template("assets.html")

if __name__ == "__main__":
    app.run(debug=True)
