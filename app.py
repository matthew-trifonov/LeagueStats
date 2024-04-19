from flask import Flask, render_template, request
from stats import get_stats

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        winrate_criteria = request.form['winrate']
        sorted_champ_dict = get_stats(name, winrate_criteria)
        print(sorted_champ_dict)
        return render_template('partials/StatsView.html', sorted_champ_dict = sorted_champ_dict)
        
    return render_template('index.html')
