import os
import shutil
import subprocess
import re
from bs4 import BeautifulSoup

# Set initial paths
initial_path = os.path.join(os.getcwd(), "Application")
mods_path = os.path.join(os.getcwd(), "Mods")
flags_file = os.path.join(os.getcwd(), "flags.cfg")

# Find window.html file
def find_window_html(path):
    for root, dirs, files in os.walk(path):
        if "window.html" in files:
            return os.path.join(root, "window.html")

window_html_path = find_window_html(initial_path)
if window_html_path:
    window_html_dir = os.path.dirname(window_html_path)

    # Delete all existing mod copies with prefix "mod_"
    for filename in os.listdir(window_html_dir):
        if filename.startswith("mod_") and filename.endswith(".js"):
            os.remove(os.path.join(window_html_dir, filename))

    # Delete all existing script tags with prefix "mod_"
    with open(window_html_path, "r") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")
    body_tag = soup.find("body")
    script_tags = body_tag.find_all("script") if body_tag else []
    for script_tag in script_tags:
        if script_tag.has_attr("src") and script_tag["src"].startswith("mod_"):
            script_tag.decompose()

    # Create new mod copies and add them to script tags
    for mod_file in os.listdir(mods_path):
        if mod_file.endswith(".js"):
            src_file = os.path.join(mods_path, mod_file)
            dst_file = os.path.join(window_html_dir, f"mod_{mod_file}")
            shutil.copyfile(src_file, dst_file)

            js_file_url = f"mod_{mod_file}"
            new_script_tag = soup.new_tag("script", src=js_file_url)
            body_tag.append(new_script_tag)
            body_tag.append("\n")

    # Save changes to window.html
    with open(window_html_path, "w") as file:
        file.write(str(soup))

    # Launch Vivaldi with flags
    vivaldi_path = os.path.join(initial_path, "vivaldi.exe")

    if os.path.exists(flags_file):
        with open(flags_file, "r") as flags:
            flags_content = flags.read()
            flags_list = re.findall(r'--\S+', flags_content)
        subprocess.Popen([vivaldi_path] + flags_list)
    # If flags.cfg doesn't exist
    else:
        subprocess.Popen([vivaldi_path])