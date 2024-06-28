import click
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
from prompt_toolkit import prompt
from code2prompt.utils.is_binary import is_binary
from code2prompt.utils.generate_markdown_content import generate_markdown_content
from code2prompt.utils.is_filtered import is_filtered
from code2prompt.utils.is_ignored import is_ignored
from code2prompt.utils.parse_gitignore import parse_gitignore
from code2prompt.process_file import process_file
from code2prompt.write_output import write_output
from code2prompt.template_processor import load_template, process_template, get_user_inputs

@click.command()
@click.option("--path", "-p", type=click.Path(exists=True), required=True, help="Path to the directory to navigate.")
@click.option("--output", "-o", type=click.Path(), help="Name of the output Markdown file.")
@click.option("--gitignore", "-g", type=click.Path(exists=True), help="Path to the .gitignore file.")
@click.option("--filter", "-f", type=str, help='Comma-separated filter patterns to include files (e.g., "*.py,*.js").')
@click.option("--exclude", "-e", type=str, help='Comma-separated patterns to exclude files (e.g., "*.txt,*.md").')
@click.option("--case-sensitive", is_flag=True, help="Perform case-sensitive pattern matching.")
@click.option("--suppress-comments", "-s", is_flag=True, help="Strip comments from the code files.", default=False)
@click.option("--line-number", "-ln", is_flag=True, help="Add line numbers to source code blocks.", default=False)
@click.option("--no-codeblock", is_flag=True, help="Disable wrapping code inside markdown code blocks.")
@click.option("--template", "-t", type=click.Path(exists=True), help="Path to a Jinja2 template file for custom prompt generation.")
def create_markdown_file(path, output, gitignore, filter, exclude, suppress_comments, case_sensitive, line_number, no_codeblock, template):
    path = Path(path)
    gitignore_path = Path(gitignore) if gitignore else path / ".gitignore"
    gitignore_patterns = parse_gitignore(gitignore_path)
    gitignore_patterns.add(".git")

    files_data = []
    for file_path in path.rglob("*"):
        if (
            file_path.is_file()
            and not is_ignored(file_path, gitignore_patterns, path)
            and is_filtered(file_path, filter, exclude, case_sensitive)
            and not is_binary(file_path)
        ):
            result = process_file(file_path, suppress_comments, line_number, no_codeblock)
            if result:
                files_data.append(result)

    if template:
        template_content = load_template(template)
        user_inputs = get_user_inputs(template_content)
        content = process_template(template_content, files_data, user_inputs)
    else:
        content = generate_markdown_content(files_data, no_codeblock)

    write_output(content, output)

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    create_markdown_file()
