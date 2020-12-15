import os
from flask import Flask, render_template
from jinja2 import FileSystemLoader


# this_file_parent_dir = os.path.dirname(__file__)
# html_root_path = os.path.join(this_file_parent_dir, "htmlroot")

app = Flask(__name__, static_folder="templates/assets")
# app.jinja_loader = FileSystemLoader(html_root_path)


@app.route("/test_site")
def RunTest():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
