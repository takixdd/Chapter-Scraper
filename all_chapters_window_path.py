from flask import Flask, render_template_string, send_from_directory, request, redirect, url_for
import webbrowser
import os
import re

app = Flask(__name__)

# Initialize global variables
folder_names = []
current_page_index = 0


@app.route('/')
def index():
    global folder_names, current_page_index

    current_folder = folder_names[current_page_index]
    folder_name = os.path.basename(current_folder)  # Get the name of the current folder

    # Get a list of image filenames in the current directory
    image_files = sorted(
        [f for f in os.listdir(current_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))],
        key=lambda x: int(re.search(r'\d+', x).group()))

    # Construct image paths
    image_paths = ["/image/{}/{}".format(current_page_index, filename) for filename in image_files]

    # Generate options for the dropdown menu
    dropdown_options = [(i, os.path.basename(folder)) for i, folder in enumerate(folder_names)]

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" type="text/css" href=" {{ url_for('static', filename='style.css') }}">
        <title>{{ folder_name }}</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: #f2f2f2;
            }
            .image-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 10px;
            }
            img {
                max-width: 100%;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <h1>{{ folder_name }}</h1>
        <div>
            <form action="{{ url_for('navigate_page') }}" method="post" class="custom-dropdown">
            <select name="page_index">
                    {% for index, option in dropdown_options %}
            <option value="{{ index }}" {% if index == current_page_index %} selected {% endif %}>{{ option }}</option>
                     {% endfor %}
            </select>
            <button type="submit">Go</button>
        </form>
            <div class="nav-buttons">
        <form action="{{ url_for('prev_page') }}" method="post">
            <input type="submit" value="Previous Page">
        </form>
        <form action="{{ url_for('next_page') }}" method="post">
            <input type="submit" value="Next Page">
        </form>
    </div>
        </div>
        <div class="image-container">
            {% for image_path in image_paths %}
                <img src="{{ image_path }}" alt="Image">
            {% endfor %}
        </div>
         <div>
            <form action="{{ url_for('navigate_page') }}" method="post" class="custom-dropdown">
            <select name="page_index">
                    {% for index, option in dropdown_options %}
            <option value="{{ index }}" {% if index == current_page_index %} selected {% endif %}>{{ option }}</option>
                     {% endfor %}
            </select>
            <button type="submit">Go</button>
        </form>
            <div class="nav-buttons">
        <form action="{{ url_for('prev_page') }}" method="post">
            <input type="submit" value="Previous Page">
        </form>
        <form action="{{ url_for('next_page') }}" method="post">
            <input type="submit" value="Next Page">
        </form>
    </div>
        </div>
    </body>
    </html>
    """, folder_name=folder_name, image_files=image_files, image_paths=image_paths, dropdown_options=dropdown_options,
                                  current_page_index=current_page_index)


@app.route('/image/<int:page>/<path:filename>')
def get_image(page, filename):
    return send_from_directory(folder_names[page], filename)


@app.route('/navigate_page', methods=['POST'])
def navigate_page():
    global current_page_index
    current_page_index = int(request.form['page_index'])
    return redirect(url_for('index'))


@app.route('/prev_page', methods=['POST'])
def prev_page():
    global current_page_index
    if current_page_index > 0:
        current_page_index -= 1
    return redirect(url_for('index'))

@app.route('/next_page', methods=['POST'])
def next_page():
    global current_page_index
    if current_page_index < len(folder_names) - 1:
        current_page_index += 1
    return redirect(url_for('index'))


def start_flask():
    app.run(debug=True, use_reloader=False)


def all_window(new_path):
    global folder_names
    folder_path = new_path

    # Sort folder names chapter-1, chapter-2 etc
    def numerical_sort(value):
        return int(value.split('-')[-1])

    def get_sorted_folder_names(folder_path):
        folder_names = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path) and item.startswith("chapter-"):
                folder_names.append(item_path)
        folder_names.sort(key=numerical_sort)
        return folder_names

    folder_names = get_sorted_folder_names(folder_path)

    server_url = 'http://127.0.0.1:5000/'
    webbrowser.open(server_url)
    start_flask()