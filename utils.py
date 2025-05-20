import os
import asyncio
import aiofiles
from prompt import *
from google import genai
from pathlib import Path


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

with open("markdown_constant.txt", "r", encoding="utf-8") as text_file:
    MARKDOWN_CONSTANT = text_file.read()


async def get_markdown_files(folder_path: Path):
    # List of folder names to exclude
    exclude_folders = [
        "project",
        "projects",
        "assignment",
        "assignments",
        "upgrade-notice",
        "course-completion",
    ]

    # Use rglob to find all .md files and filter out the ones in excluded directories
    return [
        file
        for file in folder_path.rglob("*.md")
        if not any(exclude_folder in file.parts for exclude_folder in exclude_folders)
    ]


async def extract_modules_info(markdown_file: Path):
    current_module = None
    modules, current_resources = [], []

    async with aiofiles.open(markdown_file, "r", encoding="utf-8") as md_file:
        async for line in md_file:
            stripped_line = line.strip()

            if "## Module" in stripped_line:
                # Save the previous module if it exists
                if current_module:
                    modules.append(
                        {
                            "title": current_module,
                            "resource": "\n".join(current_resources).strip(),
                        }
                    )

                # Save the previous module if it exists
                index = stripped_line.find(":")
                current_module = stripped_line[index + 1 :].strip()
                current_resources = []

            elif stripped_line.startswith("##") and current_module:
                # Encountered another heading (not a module), so stop current capture
                modules.append(
                    {
                        "title": current_module,
                        "resource": "\n".join(current_resources).strip(),
                    }
                )
                current_module = None
                current_resources = []

            elif current_module:
                # Collect lines for the current module
                current_resources.append(line.rstrip())

    return {markdown_file: modules}


async def get_modules_content(module_titles: str, file_path: Path):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = await get_module_prompt(module_titles)
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    result = response.text.strip()

    with open(file_path, "w", encoding="utf-8") as response_file:
        response_file.write(result)

    return result


async def slugify_title(title: str) -> str:
    return (
        title.lower()
        .replace(" ", "-")
        .replace(":", "")
        .replace("/", "-")
        .replace("\\", "-")
        .replace("setting", "set")
        .replace("management", "mgt")
        .replace("application", "app")
        .replace("collecting", "collect")
        .replace("installing", "install")
        .replace("introduction", "intro")
    )


async def inject_resources(content: str, resource: str) -> str:
    index_to_add = content.find("## Expected")
    resource_section = f"## Resources 📚\n\n{resource}\n\n"
    return content[:index_to_add] + resource_section + content[index_to_add:]


async def process_module_file(module_file: dict[Path, list]):
    file_path: Path = next(iter(module_file))
    destination_folder = file_path.parent
    response_file = destination_folder / "response.md"

    modules: list[dict] = list(*module_file.values())
    module_titles = [module.get("title", "") for module in modules]
    module_resources = [module.get("resource", "") for module in modules]

    if response_file.exists():
        async with aiofiles.open(response_file, "r", encoding="utf-8") as result_file:
            markdown_contents = await result_file.read()
    else:
        markdown_contents = await get_modules_content(module_titles, response_file)

    module_contents = [
        content[content.find("\n#") + 1 :].replace("*", "-")
        for content in markdown_contents.split("```markdown")
        if content.startswith("\n#")
    ]

    write_tasks = []
    for count, content in enumerate(module_contents, start=1):
        title = await slugify_title(module_titles[count - 1])

        raw_module = await inject_resources(content, module_resources[count - 1])
        cleaned_module = await clean_after_expected(raw_module)

        module_content = cleaned_module + MARKDOWN_CONSTANT
        output_path = destination_folder / f"{count}-{title}.md"

        write_tasks.append(write_module_file(output_path, module_content))

    await asyncio.gather(*write_tasks)

    if file_path.suffix == ".md" and file_path.exists():
        file_path.unlink()
    if response_file.exists():
        response_file.unlink()


async def get_all_modules_in_files(markdown_files: list[Path]):
    all_modules = await asyncio.gather(
        *[extract_modules_info(file) for file in markdown_files]
    )
    module_files = [result for result in all_modules if list(result.values())[0]]

    # Run all module_file processing concurrently
    await asyncio.gather(
        *[process_module_file(module_file) for module_file in module_files]
    )


async def write_module_file(output_path: Path, content: str):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(output_path, "w", encoding="utf-8") as new_md_file:
        await new_md_file.write(content)
        print(f"Completed ✅: {output_path}")


async def clean_after_expected(content: str) -> str:
    stopIndex = content.find("```")
    if stopIndex:
        return content[:stopIndex]
    return content
