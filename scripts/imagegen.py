import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import re

CSV_FILE = "allthetimes.csv"
OUTPUT_DIR = "images"
FONT_PATH = "PlayfairDisplay-VariableFont_wght.ttf"
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FONT_SIZE_LARGE = 30
FONT_SIZE_SMALL = 24
MIN_FONT_SIZE = 16
PADDING = 30
BOTTOM_SPACING = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)
quotes_df = pd.read_csv(CSV_FILE)

def normalize_apostrophes(s: str) -> str:
    """
    Convert various curly quotes/apostrophes to straight ASCII.
    Helps match `'Tis` vs. `’Tis` etc.
    """
    return (s.replace("’", "'")
             .replace("‘", "'")
             .replace("“", '"')
             .replace("”", '"')
            )

def flexible_time_regex(time_string: str) -> re.Pattern:
    norm_str = normalize_apostrophes(time_string)
    norm_str_stripped = re.sub(r'^[\'"]+', '', norm_str)
    norm_str_stripped = re.sub(r'[\'"]+$', '', norm_str_stripped)

    pattern = (
        r'([\'"]?)'                
        + re.escape(norm_str_stripped) +
        r'([\.,;:!?"\']?)'          
    )
    return re.compile(pattern, re.IGNORECASE)

def mark_bold_flexible(full_text: str, time_string: str) -> str:
    norm_text = normalize_apostrophes(full_text)
    pat = flexible_time_regex(time_string)

    def replacer(m):
        entire_match = m.group(0)
        leading_quote = m.group(1) or ""
        trailing_punc = m.group(2) or ""

        middle_start = len(leading_quote)
        middle_end = len(entire_match) - len(trailing_punc)
        middle_str = entire_match[middle_start:middle_end]

        return f"{leading_quote}<b>{middle_str}</b>{trailing_punc}"

    bolded_text = pat.sub(replacer, norm_text)
    return bolded_text

def tokenize_marked_text(text: str):
    tokens = []
    pattern = r'(<b>.*?</b>)'
    parts = re.split(pattern, text)

    for part in parts:
        if not part:
            continue

        part = part.replace('\n', ' ').replace('\r', ' ')

        if part.startswith('<b>') and part.endswith('</b>'):
            # inside is bold
            inner = part[3:-4]
            # again, ensure single line
            inner = inner.replace('\n', ' ').replace('\r', ' ')
            tokens.append((inner, True))
        else:
            sub_parts = re.split(r'(\s+)', part)
            for sp in sub_parts:
                if not sp:
                    continue
                # flatten newlines
                sp = sp.replace('\n', ' ').replace('\r', ' ')
                tokens.append((sp, False))

    return tokens

def measure_line_width(draw, line_tokens, font_normal, font_bold):
    width = 0
    for token_text, is_bold in line_tokens:
        if '\n' in token_text:
            # flatten again just to be safe
            token_text = token_text.replace('\n', ' ')
        font = font_bold if is_bold else font_normal
        width += draw.textlength(token_text, font=font)
    return width

def wrap_tokens(draw, tokens, font_normal, font_bold, max_width):
    """
    Wrap tokens so lines do not exceed max_width.
    Returns a list of lines, each line is a list of (token_text, is_bold).
    """
    lines = []
    current_line = []

    for token_text, is_bold in tokens:
        token_text = token_text.replace('\n', ' ')  # just in case
        if not current_line:
            current_line = [(token_text, is_bold)]
        else:
            test_line = current_line + [(token_text, is_bold)]
            if measure_line_width(draw, test_line, font_normal, font_bold) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = [(token_text, is_bold)]

    if current_line:
        lines.append(current_line)

    return lines

def measure_total_height(num_lines, font_size, line_spacing=5):
    return (font_size + line_spacing) * num_lines

def fit_text_to_height(draw, base_text: str, time_string: str,
                       initial_font_size: int, max_width: int, max_height: int):
    marked_text = mark_bold_flexible(base_text, time_string)

    had_bold = ('<b>' in marked_text)

    norm_base = normalize_apostrophes(base_text).lower()
    norm_time = normalize_apostrophes(time_string).lower()
    if (norm_time in norm_base) and not had_bold and time_string.strip():
        print(f"[WARNING] Expected '{time_string}' to appear in text, but no <b> inserted. (Check punctuation/spelling)")

    current_font_size = initial_font_size
    line_spacing = 5

    while current_font_size >= MIN_FONT_SIZE:
        font_normal = ImageFont.truetype(FONT_PATH, current_font_size)
        font_bold = ImageFont.truetype(FONT_PATH, current_font_size)
        try:
            font_bold.set_variation_by_name('Bold')
        except:
            pass

        tokens = tokenize_marked_text(marked_text)
        wrapped_lines = wrap_tokens(draw, tokens, font_normal, font_bold, max_width)
        total_h = measure_total_height(len(wrapped_lines), current_font_size, line_spacing)

        if total_h <= max_height:
            return current_font_size, wrapped_lines, had_bold

        current_font_size -= 2

    font_size = MIN_FONT_SIZE
    lines = [[("...", False)]]
    return font_size, lines, had_bold

def get_text_dimensions(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def generate_image(quote, output_path, no_bold_files):
    image = Image.new("1", (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    base_text = quote["text"]
    text_time = quote["text-time"]
    title = quote["title"]
    author = quote["author"]

    font_small = ImageFont.truetype(FONT_PATH, FONT_SIZE_SMALL)

    _, author_h = get_text_dimensions(draw, author, font_small)
    _, title_h = get_text_dimensions(draw, title, font_small)
    bottom_section_height = author_h + title_h + BOTTOM_SPACING + 2 * PADDING
    available_height = SCREEN_HEIGHT - bottom_section_height - PADDING

    font_size_large, wrapped_lines, had_bold = fit_text_to_height(
        draw,
        base_text,
        text_time,
        FONT_SIZE_LARGE,
        SCREEN_WIDTH - 2 * PADDING,
        available_height
    )

    font_normal = ImageFont.truetype(FONT_PATH, font_size_large)
    font_bold = ImageFont.truetype(FONT_PATH, font_size_large)
    try:
        font_bold.set_variation_by_name('Bold')
    except:
        pass

    y_offset = PADDING
    line_spacing = 5
    line_height = font_size_large + line_spacing

    bold_drawn = False

    for line_tokens in wrapped_lines:
        x_offset = PADDING
        for token_text, is_bold in line_tokens:
            token_text = token_text.replace('\n', ' ')
            font = font_bold if is_bold else font_normal
            draw.text((x_offset, y_offset), token_text, font=font, fill=0)
            x_offset += draw.textlength(token_text, font=font)
            if is_bold and token_text.strip():
                bold_drawn = True
        y_offset += line_height

    author_w, author_h = get_text_dimensions(draw, author, font_small)
    title_w, title_h = get_text_dimensions(draw, title, font_small)

    author_x = SCREEN_WIDTH - author_w - PADDING
    author_y = SCREEN_HEIGHT - (author_h + title_h) - BOTTOM_SPACING - PADDING

    title_x = SCREEN_WIDTH - title_w - PADDING
    title_y = SCREEN_HEIGHT - title_h - PADDING

    draw.text((author_x, author_y), author, font=font_small, fill=0)
    draw.text((title_x, title_y), title, font=font_small, fill=0)

    image.save(output_path)

    if had_bold and not bold_drawn:
        no_bold_files.append(output_path)

def main():
    grouped = quotes_df.groupby("time-of-text")
    count = 0

    no_bold_files = []

    for time_of_text, group in grouped:
        sanitized_time = time_of_text.replace(":", "-")
        
        for index, (_, quote) in enumerate(group.iterrows(), start=1):
            if count >= 4223:
                break

            output_path = os.path.join(OUTPUT_DIR, f"{sanitized_time}_{index}.png")

            if os.path.exists(output_path):
                print(f"Skipping {output_path}, already exists.")
                count += 1
                continue

            generate_image(quote, output_path, no_bold_files)
            print(f"Generated image for {time_of_text} (Index: {index})")
            count += 1

    if no_bold_files:
        print("\n=== IMAGES WITHOUT BOLD TEXT (But Expected Some) ===")
        for path in no_bold_files:
            print(f"  {path}")
    else:
        print("\nAll images that needed bold text appear to have it!")

if __name__ == "__main__":
    main()
