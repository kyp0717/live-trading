import shutil
import os

from jinja2 import Environment
from jinja2 import FileSystemLoader

TEMPLATE_NAME = 'base.html'
OUTPUT_FILE_NAME = 'test_output.html'

class HtmlGenerator(object):
    def __init__(self, template_name):
        self.template_name = template_name
        self.env = Environment(loader=FileSystemLoader('live_templates'))

    def _build_path(self, suffix):
        # Build the full file path based on our current directory
        current_directory = os.getcwd() 
        # d = current_directory + "/live"
        # print(d)
        return os.path.join(current_directory, suffix)

    def generate(self):
        public_folder_path = self._build_path('public')
        # If the public folder exists, then throw it away so we can regenerate it
        if os.path.isdir(public_folder_path):
            shutil.rmtree(public_folder_path)
        os.mkdir(public_folder_path)

        # Get Jinja template
        # Print the search path
        print(f'search: {self.env.loader.searchpath}')
        template = self.env.get_template(self.template_name)
        with open(self._build_path('public/%s' % OUTPUT_FILE_NAME), 'w') as html_file:
            html = template.render(
                title="Sample Page",
                content="Hello World!"
            )
            # Write the rendered template to the html file
            html_file.write(html)


if __name__ == '__main__':
    html_generator = HtmlGenerator(TEMPLATE_NAME)
    html_generator.generate()