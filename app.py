from flask import Flask, request, render_template
import dataset as ds
import joblib
import os
import pandas as pd

app = Flask(__name__, template_folder='templates')

@app.cli.command("deploy_model")
def deploy_model():
    dataset = ds.get_data()
    ds.store_metrics(dataset)
    ds.build_model(dataset)
    app.run(debug=True)


if not os.path.exists(ds.model_path):
    deploy_model()

with open(ds.model_path, 'rb') as f:
    model = joblib.load(f)

try:
    query_targets = 'SELECT Target FROM target_counts'
    target_counts = pd.read_sql(query_targets, ds.engine)
    targets = target_counts.to_numpy().flatten()
except Exception as e:
    print(f"Error querying target_counts: {e}")

# Fetch all records from the category_counts table
try:
    query_categories = 'SELECT Category FROM category_counts'
    category_counts = pd.read_sql(query_categories, ds.engine)
    categories = category_counts.to_numpy().flatten()
except Exception as e:
    print(f"Error querying category_counts: {e}")

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('index.html', targets=targets, categories=categories)

    if request.method == 'POST':
        target = request.form['target']
        category = request.form['category']

        new_review = pd.DataFrame({
            'Target': [target],
            'Category': [category],
        })

        prediction = model.predict(new_review)[0]

        return render_template('index.html', targets=targets, categories=categories, original_input={'Opinion Target': target, 'Category': category}, result=prediction)    

if __name__ == '__main__':
    app.run(debug=True)
