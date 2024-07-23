from playwright.sync_api import sync_playwright
import re
import subprocess

def convert_to_say_command(text):
    # Remove <mark> tags as they're not relevant for speech
    text = re.sub(r'<mark[^>]*>', '', text)

    # Convert <break> tags to [[slnc]] commands
    text = re.sub(r'<break time=\'(\d+)ms\'/>', lambda m: f"[[slnc {int(m.group(1))}]]", text)

    # Replace <say-as> tags for individual characters with a short pause
    text = re.sub(r'<say-as interpret-as=\'characters\'>([^<]+)</say-as>',
                  lambda m: ' '.join(f"{c} [[slnc 50]]" for c in m.group(1)), text)

    # Remove any remaining XML-like tags
    text = re.sub(r'<[^>]+>', '', text)

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def scrape_mathcat_demo(latex):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://nsoiffer.github.io/MathCATDemo/")
            textarea = page.locator("#mathml-input")
            textarea.fill(latex)
            page.locator("input#Medium[name='verbosity']").check()
            page.locator("#render-button").click()
            speech_textarea = page.locator("#speech")
            speech_textarea.wait_for()
            return speech_textarea.input_value()
        finally:
            browser.close()

def get_say_command_text_from_latex(latex):
    result = scrape_mathcat_demo(latex)
    say_command_text = convert_to_say_command(result)
    return say_command_text

if __name__ == "__main__":
    print(get_say_command_text_from_latex(r"\int_x^\infty \frac{|\ln(x)|dx}{e^{3x}}"))
