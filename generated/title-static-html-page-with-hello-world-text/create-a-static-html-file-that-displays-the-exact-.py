# This Python script generates a static HTML file with the exact text "Hello World"
# using valid HTML5 structure. It ensures the file is saved with a .html extension.

def generate_hello_world_html():
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Hello World</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>'''

    with open("hello-world.html", "w") as file:
        file.write(html_content)

generate_hello_world_html()