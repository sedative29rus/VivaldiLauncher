import os
import shutil
import subprocess
import re
import glob

# Set initial paths
initial_path = os.path.join(os.getcwd(), "Application")
mods_path = os.path.join(os.getcwd(), "Mods")
flags_file = os.path.join(os.getcwd(), "flags.cfg")


# Find window.html file (fast glob, fallback to os.walk)
def find_window_html(path):
    matches = glob.glob(os.path.join(path, "*", "resources", "vivaldi", "window.html"))
    if matches:
        return matches[0]
    for root, dirs, files in os.walk(path):
        if "window.html" in files:
            return os.path.join(root, "window.html")


window_html_path = find_window_html(initial_path)
if window_html_path:
    window_html_dir = os.path.dirname(window_html_path)

    # Collect current mod_*.js files in window_html_dir
    current_mods = {}
    for f in os.listdir(window_html_dir):
        if f.startswith("mod_") and f.endswith(".js"):
            current_mods[f] = os.path.join(window_html_dir, f)

    # Collect and copy mod files from Mods/
    source_mods = {}
    if os.path.exists(mods_path):
        for root, dirs, files in os.walk(mods_path):
            for file in files:
                if file.endswith(".js"):
                    src_path = os.path.join(root, file)
                    dst_name = f"mod_{file}"
                    dst_path = os.path.join(window_html_dir, dst_name)

                    need_copy = True
                    if dst_name in current_mods:
                        src_stat = os.stat(src_path)
                        dst_stat = os.stat(dst_path)
                        if src_stat.st_size == dst_stat.st_size and src_stat.st_mtime == dst_stat.st_mtime:
                            need_copy = False

                    if need_copy:
                        shutil.copyfile(src_path, dst_path)

                    source_mods[dst_name] = dst_path

    # Remove mod_*.js that no longer have a source in Mods/
    for name, path in current_mods.items():
        if name not in source_mods:
            os.remove(path)

    # Read window.html
    with open(window_html_path, "r", encoding="utf-8") as file:
        html = file.read()

    # Remove existing mod_ script tags
    clean_html = re.sub(
        r'<script[^>]*\bsrc=["\']mod_[^"\']*["\'][^>]*></script>\s*',
        "",
        html,
    )

    # Add new mod script tags before </body>
    if source_mods:
        mod_scripts = "".join(
            f'<script src="{name}"></script>\n' for name in sorted(source_mods)
        )
        new_html = clean_html.replace("</body>", mod_scripts + "</body>")
    else:
        new_html = clean_html

    # Only write if changed
    if new_html != html:
        with open(window_html_path, "w", encoding="utf-8") as file:
            file.write(new_html)

    # Launch Vivaldi with flags
    vivaldi_path = os.path.join(initial_path, "vivaldi.exe")
    if not os.path.exists(vivaldi_path):
        print(f"vivaldi.exe not found at: {vivaldi_path}")
        exit()

    cmd = [vivaldi_path]
    if os.path.exists(flags_file):
        with open(flags_file, "r") as flags:
            flags_list = [
                line.strip()
                for line in flags
                if line.strip() and not line.strip().startswith("#")
            ]
        cmd.extend(flags_list)

    subprocess.Popen(cmd)
