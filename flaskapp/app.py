from flask import Flask, render_template
from dotenv import load_dotenv
import sys

# import benchmark as bm
from utils import benchmark as bm
from utils import html_generator as gen


# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/kepl/work/live-trading/flaskapp/utils')

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def home():
    return render_template("home.html")



if __name__ == "__main__":
    
    spybm = bm.Benchmark('SPY', live=False)
    d = spybm.run()
    spy_html = gen.HtmlGenerator("./templates/cards/spy_tmpl.html", d.__dict__ , "spy_out.html")
    spy_html.generate()
    # app.run(debug=True)
