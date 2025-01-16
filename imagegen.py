import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

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
BOLD_INCREASE = 0  # Set to 0 to maintain same font size but use weight for bold

os.makedirs(OUTPUT_DIR, exist_ok=True)
quotes_df = pd.read_csv(CSV_FILE)

def wrap_text(draw, text, font, max_width):
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        width = draw.textlength(test_line, font=font)
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

def get_text_dimensions(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def calculate_text_height(draw, wrapped_text, font_size_large):
    font_large = ImageFont.truetype(FONT_PATH, font_size_large)
    lines = wrapped_text.split("\n")
    return len(lines) * (font_size_large + 5)

def fit_text_to_height(draw, text, initial_font_size, max_width, max_height):
    current_font_size = initial_font_size
    
    while current_font_size >= MIN_FONT_SIZE:
        font = ImageFont.truetype(FONT_PATH, current_font_size)
        wrapped_text = wrap_text(draw, text, font, max_width)
        total_height = calculate_text_height(draw, wrapped_text, current_font_size)
        
        if total_height <= max_height:
            return current_font_size, wrapped_text
            
        current_font_size -= 2
    
    # If we get here, even the minimum font size doesn't fit
    # Truncate the text and add ellipsis
    font = ImageFont.truetype(FONT_PATH, MIN_FONT_SIZE)
    words = text.split()
    truncated_text = ""
    
    for i in range(len(words)):
        test_text = " ".join(words[:-(i+1)]) + "..."
        wrapped_test = wrap_text(draw, test_text, font, max_width)
        total_height = calculate_text_height(draw, wrapped_test, MIN_FONT_SIZE)
        
        if total_height <= max_height:
            return MIN_FONT_SIZE, wrapped_test
            
    return MIN_FONT_SIZE, "..."  # Worst case: nothing fits

def generate_image(quote, output_path):
    image = Image.new("1", (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    text = quote["text"]
    text_time = quote["text-time"]
    title = quote["title"]
    author = quote["author"]

    # Calculate available height for main text
    font_small = ImageFont.truetype(FONT_PATH, FONT_SIZE_SMALL)
    author_height = get_text_dimensions(draw, author, font_small)[1]
    title_height = get_text_dimensions(draw, title, font_small)[1]
    bottom_section_height = author_height + title_height + BOTTOM_SPACING + (2 * PADDING)
    available_height = SCREEN_HEIGHT - bottom_section_height - PADDING

    # Fit text to available height
    font_size_large, wrapped_text = fit_text_to_height(
        draw, text, 
        FONT_SIZE_LARGE, 
        SCREEN_WIDTH - (2 * PADDING),
        available_height
    )

    # Create fonts with the determined size, using font variation for bold instead of size
    font_large = ImageFont.truetype(FONT_PATH, font_size_large)
    bold_font = ImageFont.truetype(FONT_PATH, font_size_large)
    try:
        # Try to set the font weight if the font supports it
        bold_font.set_variation_by_name('Bold')
    except:
        pass  # If font doesn't support variations, it will still be readable

    # Draw the text
    lines = wrapped_text.split("\n")
    y_offset = PADDING

    for line in lines:
        if text_time in line:
            parts = line.split(text_time)
            x_offset = PADDING
            
            for i, part in enumerate(parts):
                draw.text((x_offset, y_offset), part, font=font_large, fill=0)
                x_offset += draw.textlength(part, font=font_large)
                
                if i < len(parts) - 1:
                    # Draw text_time at the same vertical position
                    draw.text((x_offset, y_offset), text_time, font=bold_font, fill=0)
                    x_offset += draw.textlength(text_time, font=bold_font)
        else:
            draw.text((PADDING, y_offset), line, font=font_large, fill=0)
        y_offset += font_size_large + 5

    # Draw author and title
    author_x = SCREEN_WIDTH - get_text_dimensions(draw, author, font_small)[0] - PADDING
    author_y = SCREEN_HEIGHT - author_height - title_height - BOTTOM_SPACING - PADDING

    title_x = SCREEN_WIDTH - get_text_dimensions(draw, title, font_small)[0] - PADDING
    title_y = SCREEN_HEIGHT - title_height - PADDING

    draw.text((author_x, author_y), author, font=font_small, fill=0)
    draw.text((title_x, title_y), title, font=font_small, fill=0)

    image.save(output_path)

def main():
    grouped = quotes_df.groupby("time-of-text")
    count = 0

    for time_of_text, group in grouped:
        sanitized_time = time_of_text.replace(":", "-")
        
        for index, (_, quote) in enumerate(group.iterrows(), start=1):
            if count >= 10:
                return
            output_path = os.path.join(OUTPUT_DIR, f"{sanitized_time}_{index}.png")
            generate_image(quote, output_path)
            print(f"Generated image for {time_of_text} (Index: {index})")
            count += 1

if __name__ == "__main__":
    main()