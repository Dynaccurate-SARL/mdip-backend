import argparse
import os
import re

def inline_assets_in_directory(directory, recursive=True):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_path = os.path.join(root, file)
                inline_assets(html_path)
        if not recursive:
            break

def inline_assets(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    base_dir = os.path.dirname(html_path)
    modified = False

    # Inline CSS
    def replace_css(match):
        href = match.group(1)
        css_path = os.path.join(base_dir, href)
        if os.path.isfile(css_path):
            with open(css_path, 'r', encoding='utf-8') as css_file:
                css_content = css_file.read()
                return f"<style>{css_content}</style>"
        return match.group(0)

    # Inline JS
    def replace_js(match):
        src = match.group(1)
        defer = " defer" if "defer" in match.group(0) else ""
        js_path = os.path.join(base_dir, src)
        if os.path.isfile(js_path):
            with open(js_path, 'r', encoding='utf-8') as js_file:
                js_content = js_file.read()
                return f"<script{defer}>{js_content}</script>"
        return match.group(0)

    # Regex to capture CSS and JS files
    css_pattern = re.compile(r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>', re.IGNORECASE)
    js_pattern = re.compile(r'<script\s+[^>]*src=["\']([^"\']+)["\'][^>]*>\s*</script>', re.IGNORECASE)

    new_html = css_pattern.sub(replace_css, html)
    new_html = js_pattern.sub(replace_js, new_html)

    if new_html != html:
        output_path = os.path.join(base_dir, os.path.basename(html_path))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f"[✔] Inlined: {html_path} → {output_path}")
    else:
        print(f"[!] No modifications: {html_path}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Inline CSS and JS assets in HTML files.")
    parser.add_argument('--path', required=True,
                        help="Path to the directory containing HTML files.")
    args = parser.parse_args()

    inline_assets_in_directory(args.path)
