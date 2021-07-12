""" Basic flask application for distributing modded minecraft client instances. """
import os
import json

from flask import Flask, request, render_template, redirect, url_for, send_file

app = Flask(__name__)


def counter():
    i = 0
    while True:
        i += 1
        yield i


INSTANCE_IDS = counter()

INSTANCE_DIR = os.getenv("INSTANCE_DIR", f"{os.getcwd()}/instances")


def get_meta_info(instance_id):
    """Get meta data for an instance."""
    with open(f"{INSTANCE_DIR}/{instance_id}/meta.json") as meta_file:
        return json.load(meta_file)


@app.route("/")
def main_page():
    return render_template("index.html")


@app.route("/instances")
def view_instances():

    instances = [get_meta_info(instance_id) for instance_id in os.listdir(INSTANCE_DIR)]

    return render_template("instances.html", instances=instances)


@app.route("/instances/<int:instance_id>")
def view_instance(instance_id):
    """View details about a specific instance"""

    return render_template("instance.html", instance_info=get_meta_info(instance_id))


@app.route("/instances/<int:instance_id>/download")
def download_instance(instance_id):
    """Download the instance"""

    return send_file(f"{INSTANCE_DIR}/{instance_id}/instance.zip")


@app.route("/instances/upload", methods=["GET", "POST"])
def upload():
    """Upload a multimc instance."""
    if request.method == "GET":
        return render_template("upload.html")

    file = request.files["file"]
    instance_name = request.form["name"]

    instance_id = next(INSTANCE_IDS)
    instance_dir = f"{INSTANCE_DIR}/{instance_id}"
    while os.path.isdir(instance_dir):
        instance_id = next(INSTANCE_IDS)
        instance_dir = f"{INSTANCE_DIR}/{instance_id}"

    os.makedirs(instance_dir)

    instance_filename = f"{instance_dir}/instance.zip"
    print(f"Saving instance to: {instance_filename}")
    file.save(instance_filename)

    with open(f"{instance_dir}/meta.json", "w") as meta_file:
        json.dump(
            {
                "instance_id": instance_id,
                "instance_name": instance_name,
                "file_name": file.filename,
            },
            meta_file,
        )

    return redirect(url_for("view_instance", instance_id=instance_id))


if __name__ == "__main__":
    app.run(debug=True)
