from flask import Flask, render_template_string, send_from_directory
import webbrowser
import os
import re

app = Flask(__name__)


@app.route('/')
def index():
    global folder_path
    # Get a list of image filenames in the directory
    image_files = sorted(
        [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))],
        key=lambda x: int(re.search(r'\d+', x).group()))
    print("Image files:", image_files)  # Debug print statement

    image_paths = ["/image/" + filename for filename in image_files]
    print("Image paths:", image_paths)  # Debug print statement

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Latest Chapter</title>
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
                padding: 20px;
            }
            img {
                max-width: 100%;
                margin-bottom: 20px;
            }
        </style>
        <script>
            var imagePaths = {{ image_paths | tojson | safe }};
            console.log("Image paths:", imagePaths);

            var currentIndex = 0;

            function showImage(index) {
                var img = document.getElementById("image");
                img.src = imagePaths[index];
                currentIndex = index;
            }

            function nextImage() {
                currentIndex = (currentIndex + 1) % imagePaths.length;
                showImage(currentIndex);
            }

            function prevImage() {
                currentIndex = (currentIndex - 1 + imagePaths.length) % imagePaths.length;
                showImage(currentIndex);
            }

            document.addEventListener("DOMContentLoaded", function() {
                showImage(currentIndex);
            });

            document.addEventListener("keydown", function(event) {
                if (event.key === "ArrowRight") {
                    nextImage();
                } else if (event.key === "ArrowLeft") {
                    prevImage();
                }
            });
        </script>
    </head>
    <body>
        <div class="image-container">
            {% for image_path in image_paths %}
                <img src="{{ image_path }}" alt="Image">
            {% endfor %}
        </div>
    </body>
    </html>
    """, image_files=image_files, image_paths=image_paths)


@app.route('/image/<path:filename>')
def get_image(filename):
    return send_from_directory(folder_path, filename)


def start_flask():
    global folder_path
    app.run(debug=True, use_reloader=False)


def latest_window(new_path):
    global folder_path
    folder_path = new_path
    server_url = 'http://127.0.0.1:5000/'
    webbrowser.open(server_url)
    start_flask()
