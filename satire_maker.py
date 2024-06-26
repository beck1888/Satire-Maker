import openai
import markdown
import pdfkit
import os
import json
import random
import terminal_tools as tt
# from image_maker import generate_image_from_headline

def verify_api_key() -> None:
    # Verify an environment file exists
    if ".env" not in os.listdir():
        exit("ERROR: No environment file found. Please create a .env file with your OpenAI API key.")

    # Verify there is an API key in the environment file
    with open(".env") as f:
        if "OPENAI_API_KEY=\"" not in f.read():
            exit("ERROR: No API key found in the .env file. Please add your OpenAI API key to the .env file like this: OPENAI_API_KEY=\"your_api_key_here\".")

path_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'  # Path based to installation
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def make_a_satire_article(idea: str) -> str:
    client = openai.OpenAI()

    with open("bot_instructions.txt") as f:
        bot_instructions = f.read()

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": bot_instructions},
        {"role": "user", "content": idea},
    ]
    )

    story_json = completion.choices[0].message.content

    return story_json

def make_md_version_of_story(story_dict: dict) -> str: # Markdown is easier to layout
    # Create variables from the dictionary

    # These assignments often raise KeyErrors but still contain the correct information so using try/except statements should just hide errors
    try:
        headline = story_dict["headline"]
    except:
        headline = ""

    try:
        location = story_dict["location"]
    except:
        location = ""

    try:
        story = story_dict["story"]
    except:
        story = ""

    try:
        recommended_headline_1 = story_dict["recommended_headlines"][0]
    except:
        recommended_headline_1 = ""

    try:
        recommended_headline_2 = story_dict["recommended_headlines"][1]
    except:
        recommended_headline_2 = ""

    # Pick two random up next headline intros
    all_headline_intros = ["This just in:", "Readers also liked:", "You might like:", "Related and funny:", "Check out:", "Breaking news:", "Shocking:", "Follow up:", "Consider checking out:", "Take a look at:"]

    headline_intros = random.sample(all_headline_intros, 2)

    # Create the markdown version of the story
    md_story = f"""
    # {headline.upper()}

    *{location}* - {story}

    ---

    **{headline_intros[0].upper()}** {recommended_headline_1.title()}

    **{headline_intros[1].upper()}** {recommended_headline_2.title()}
    """

    # Make the headline name for friendly to operating systems
    new_headline = ""
    for char in headline:
        if char.lower() in "abcdefghijklmnopqrstuvwxyz":
            new_headline += char
        elif char == " ":
            new_headline += "_"
        else:
            pass

    headline = new_headline.capitalize()

    # Save the markdown version of the story
    with open(f"articles/{headline}.md", "w") as f:
        f.write(md_story)

    # Clean up the markdown file
    with open(f"articles/{headline}.md", "r") as f:
        lines = f.readlines()

    with open(f"articles/{headline}.md", "w") as f:
        for line in lines:
            f.write(line.replace("    ", "")) # Remove extra spaces for proper formatting

    # Return where the story is saved
    return f"articles/{headline}.md"

def convert_md_to_pdf(md_file: str) -> None:
    # Read the Markdown file
    with open(md_file, "r") as f:
        md_content = f.read()
    
    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content)
    
    # Convert HTML to PDF
    pdf_file = f"{md_file[:-3]}.pdf"
    # pdfkit.from_string(html_content, pdf_file) # Doesn't work, needs a set configuration
    pdfkit.from_string(html_content, pdf_file, configuration=config)

def main(idea_for_satire: str = "", tries: int = 1) -> None: # Allows the script to try again if it fails to parse the prompt
    verify_api_key()

    if tries > 4:
        exit("Your input is causing problems. Please try again with a different prompt.")
    else:
        # print(f"Attempt {tries}")
        pass

    if idea_for_satire == "": 
        idea_for_satire = input("Enter an idea for a satire story or press enter to automatically generate one: ")
        if idea_for_satire == "":
            with open("headline_ideas.json") as f:
                headline_ideas = json.load(f)
            idea_for_satire = random.choice(headline_ideas)
            # print(f"Auto generated idea: {idea_for_satire}")

    story_maker = tt.Spinner(make_a_satire_article) # Pass the function as an argument
    # print("Contacting the API...")
    story = story_maker.run(idea_for_satire) # Pass the idea as an argument and show a spinner while the function is running
    # print("API response received.")

    # Initialize the story dictionary to avoid a unbound error
    story_dict = {}

    # Convert the response string to a dictionary
    try:
        story_dict = eval(story)
        # print("Parsed API response successfully.")
    except SyntaxError:
        # print("Unexpected API response. Trying again...")
        main(idea_for_satire, tries + 1)

    # Turn the story into a formatted markdown file
    # print("Creating markdown file...")
    saved_file = make_md_version_of_story(story_dict)
    # print("Markdown file created.")

    # Convert the markdown file to a pdf
    # print("Converting markdown to pdf...")
    make_pdf = tt.Spinner(convert_md_to_pdf)
    make_pdf.run(saved_file)
    # print("Markdown converted to pdf.")

    # Clean up all markdown files in the articles directory
    # print("Cleaning up markdown files...")
    for file in os.listdir("articles"):
        if file.endswith(".md"):
            os.remove(f"articles/{file}")
    
    # Show the pdf
    # print("Opening pdf...")

    # Clean up possible old pdf junk file
    try:
        os.remove("articles/.pdf")
    except:
        pass

    # Open the pdf
    saved_file = saved_file.removeprefix('articles/').removesuffix('.md')
    os.system(f"open articles/{saved_file}.pdf")
    # os.system(f"open {saved_file.removesuffix('.md').removesuffix('.pdf')}.pdf")
    # print("Pdf opened.")

    # print("Done!")

if __name__ == "__main__":
    main()