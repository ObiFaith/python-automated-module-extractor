async def get_module_prompt(module_titles: list[str]) -> str:
    module_titles_str = "\n".join(f"- {title}" for title in module_titles)

    with open("content_template.md", "r", encoding="utf-8") as content_file:
        CONTENT_TEMPLATE = content_file.read()

    return f"""
        You are an expert technical writer. Based on the list of module titles below, generate well-structured markdown content for each module, following the format example provided.

        Each module should:
        - Start with the **exact title** as a `#` heading (H1)
        - Include these sections (in this order): Prerequisite, Time Estimate, Instruction, Expected Learning Outcome
        - Wrap each module in triple backticks (```markdown) for separation
        - The **Instruction** section should be a single sentence that briefly introduces the module
        - Ensure bullet points use `-` instead of `*`
        - Do not include any introductory or explanatory text outside of the code blocks

        ### 🧾 Module Titles:
        {module_titles_str}

        ### 📘 Example Format (use exactly):
        ```markdown
        {CONTENT_TEMPLATE}
         """
