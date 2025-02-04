import shutil
import os

from jinja2 import Environment
from jinja2 import FileSystemLoader


class HtmlGenerator(object):
    def __init__(self, template_name, input_data: dict, outname: str):
        self.template_name = template_name
        self.template_output = outname
        self.data = input_data
        self.env = Environment(loader=FileSystemLoader(['templates/cards', 'templates']))

    def _build_path(self, suffix):
        # Build the full file path based on our current directory
        current_directory = os.getcwd()
        return os.path.join(current_directory, suffix)

    def generate(self):

        # Get Jinja template
        # Print the search path
        print(f'search: {self.env.loader.searchpath}')
        print(self.data)
        template = self.env.get_template(self.template_name)
        with open(f'./flaskapp/templates/{self.template_output}', 'w') as html_file:
            html = template.render(self.data)
            # Write the rendered template to the html file
            html_file.write(html)

## usage
# if __name__ == '__main__':
#     html_generator = HtmlGenerator(TEMPLATE_NAME)
#     html_generator.generate()