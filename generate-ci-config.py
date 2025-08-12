import os
from jinja2 import Template  # type: ignore


def list_folders(directory):
    folders = [
        name
        for name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, name))
    ]
    return folders


def create_env():
    changed_folders = os.getenv("CHANGED_FOLDERS").strip().split(" ")
    changed_projects = [s for s in changed_folders if "p-" in s]
    vars_map = {
        "changed_folders": changed_folders,
        "changed_projects": changed_projects,
        "folders": list_folders("."),
    }
    print(vars_map)
    return vars_map


def read_template():
    with open("cicd-template.j2", "r", encoding="UTF-8") as file:
        return file.read()


def write_config(template):
    with open("generated-config.yml", "w", encoding="UTF-8") as file:
        file.write(template)


def generate_config():
    input_data = read_template()
    render_template = Template(input_data)
    config_content = render_template.render(**create_env())
    write_config(config_content)
    print("Create generated-config.yml successfully!")


if __name__ == "__main__":
    generate_config()