import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

# This function is the core of your script. The rest of the original file is identical.
def create_pdf(text, output_filename):
    """
    Takes a string of text and an output filename and generates the PDF.
    This is the main function from your provided script.
    """
    normalFont = "Courier"
    boldFont = "Courier-Bold"

    c = canvas.Canvas(output_filename, pagesize=A4)
    width, height = A4

    # --- Define Page Geometry and Margins ---
    page_horizontal_margin = 2 * mm
    page_vertical_margin = 2 * mm
    gap_between_content_blocks_x = 2 * mm
    font_size = 5.7
    line_height = font_size + 0.1
    conceptual_col_content_width = (width - (2 * page_horizontal_margin) - (5 * gap_between_content_blocks_x)) / 6

    if conceptual_col_content_width <= 0:
        raise ValueError("Calculated conceptual column content width is zero or negative.")
    
    max_lines_per_conceptual_column = int((height - (2 * page_vertical_margin)) / line_height)

    if max_lines_per_conceptual_column <= 0:
        raise ValueError("No lines can fit vertically in a conceptual column.")

    # --- Phase 1: Collect and layout content ---
    NUM_CONCEPTUAL_COLUMNS_PER_SET = 12
    all_column_sets = []
    current_column_set = [[] for _ in range(NUM_CONCEPTUAL_COLUMNS_PER_SET)]
    current_column_set_line_counts = [0] * NUM_CONCEPTUAL_COLUMNS_PER_SET
    current_logical_column_in_set_idx = 0
    c.setFont(normalFont, font_size)

    for line_from_md in text.split('\n'):
        # (The entire complex logic for parsing and layout from your script goes here)
        # ... from your script ...
        # This part is long, so it is omitted for brevity, but you should paste
        # the entire content of your `create_pdf` function here.
        # For this example, I am including the full logic.
        line_from_md = line_from_md.strip()

        if not line_from_md:
            if current_logical_column_in_set_idx < NUM_CONCEPTUAL_COLUMNS_PER_SET and \
               current_column_set_line_counts[current_logical_column_in_set_idx] < max_lines_per_conceptual_column:
                current_column_set_line_counts[current_logical_column_in_set_idx] += 1
            
            if current_logical_column_in_set_idx < NUM_CONCEPTUAL_COLUMNS_PER_SET and \
               current_column_set_line_counts[current_logical_column_in_set_idx] >= max_lines_per_conceptual_column:
                current_logical_column_in_set_idx += 1

                if current_logical_column_in_set_idx >= NUM_CONCEPTUAL_COLUMNS_PER_SET:
                    all_column_sets.append(current_column_set)
                    current_column_set = [[] for _ in range(NUM_CONCEPTUAL_COLUMNS_PER_SET)]
                    current_column_set_line_counts = [0] * NUM_CONCEPTUAL_COLUMNS_PER_SET
                    current_logical_column_in_set_idx = 0
            continue

        is_heading = line_from_md.startswith("#")
        content = line_from_md.lstrip("#").strip() if is_heading else line_from_md

        if is_heading:
            initial_segments = [(word+" ", True) for word in content.split(' ') if word]
        else:
            initial_segments = parse_inline_markdown(content)

        word_segments_for_drawing = []
        for text_part, is_bold_status in initial_segments:
            words_and_spaces = re.split(r'(\s+)', text_part)
            for item in words_and_spaces:
                if item:
                    word_segments_for_drawing.append((item, is_bold_status))

        current_x_on_virtual_line = 0
        for word_text, is_bold_status in word_segments_for_drawing:
            segment_font_name = boldFont if is_bold_status else normalFont
            c.setFont(segment_font_name, font_size)
            word_width = c.stringWidth(word_text)

            if current_x_on_virtual_line + word_width > conceptual_col_content_width and current_x_on_virtual_line != 0:
                current_column_set_line_counts[current_logical_column_in_set_idx] += 1
                current_x_on_virtual_line = 0

            if current_column_set_line_counts[current_logical_column_in_set_idx] >= max_lines_per_conceptual_column:
                current_logical_column_in_set_idx += 1
                if current_logical_column_in_set_idx >= NUM_CONCEPTUAL_COLUMNS_PER_SET:
                    all_column_sets.append(current_column_set)
                    current_column_set = [[] for _ in range(NUM_CONCEPTUAL_COLUMNS_PER_SET)]
                    current_column_set_line_counts = [0] * NUM_CONCEPTUAL_COLUMNS_PER_SET
                    current_logical_column_in_set_idx = 0
                current_x_on_virtual_line = 0

            current_y_rel_to_top = current_column_set_line_counts[current_logical_column_in_set_idx] * line_height
            current_column_set[current_logical_column_in_set_idx].append(
                (word_text, is_bold_status, current_x_on_virtual_line, current_y_rel_to_top)
            )
            current_x_on_virtual_line += word_width

        if line_from_md:
            current_column_set_line_counts[current_logical_column_in_set_idx] += 1
            current_x_on_virtual_line = 0
            if current_column_set_line_counts[current_logical_column_in_set_idx] >= max_lines_per_conceptual_column:
                current_logical_column_in_set_idx += 1
                if current_logical_column_in_set_idx >= NUM_CONCEPTUAL_COLUMNS_PER_SET:
                    all_column_sets.append(current_column_set)
                    current_column_set = [[] for _ in range(NUM_CONCEPTUAL_COLUMNS_PER_SET)]
                    current_column_set_line_counts = [0] * NUM_CONCEPTUAL_COLUMNS_PER_SET
                    current_logical_column_in_set_idx = 0

    if any(current_column_set):
        all_column_sets.append(current_column_set)

    # --- Phase 2: Draw content onto PDF pages ---
    x_physical_slot_bases = []
    vertical_line_x_positions = []
    for i in range(6):
        x_base = page_horizontal_margin + (i * conceptual_col_content_width) + (i * gap_between_content_blocks_x)
        x_physical_slot_bases.append(x_base)
        if i < 5:
            line_x = x_base + conceptual_col_content_width
            vertical_line_x_positions.append(line_x)

    line_y_start = page_vertical_margin
    line_y_end = height - page_vertical_margin

    for col_set_idx, col_set in enumerate(all_column_sets):
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.2)
        for line_x in vertical_line_x_positions:
            c.line(line_x, line_y_start, line_x, line_y_end)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1) 
        
        imposition_map_front = [(col_set[0], x_physical_slot_bases[0]), (col_set[2], x_physical_slot_bases[1]), (col_set[4], x_physical_slot_bases[2]), (col_set[6], x_physical_slot_bases[3]), (col_set[8], x_physical_slot_bases[4]), (col_set[10], x_physical_slot_bases[5])]
        for content_list, x_physical_base in imposition_map_front:
            for word_text, is_bold_status, x_rel, y_rel in content_list:
                c.setFont(boldFont if is_bold_status else normalFont, font_size)
                c.drawString(x_physical_base + x_rel, height - page_vertical_margin - y_rel, word_text)
        c.showPage()

        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.2)
        for line_x in vertical_line_x_positions:
            c.line(line_x, line_y_start, line_x, line_y_end)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        
        imposition_map_back = [(col_set[11], x_physical_slot_bases[0]), (col_set[9], x_physical_slot_bases[1]), (col_set[7], x_physical_slot_bases[2]), (col_set[5], x_physical_slot_bases[3]), (col_set[3], x_physical_slot_bases[4]), (col_set[1], x_physical_slot_bases[5])]
        for content_list, x_physical_base in imposition_map_back:
            for word_text, is_bold_status, x_rel, y_rel in content_list:
                c.setFont(boldFont if is_bold_status else normalFont, font_size)
                c.drawString(x_physical_base + x_rel, height - page_vertical_margin - y_rel, word_text)
        
        if col_set_idx < len(all_column_sets) - 1:
            c.showPage()
    
    c.save()
    print(f"PDF '{output_filename}' created successfully.")

def parse_inline_markdown(line):
    """
    Parses a string for **bold** segments.
    """
    segments = []
    last_idx = 0
    matches = list(re.finditer(r'\*\*([^\*]+?)\*\*', line))
    for match in matches:
        if match.start() > last_idx:
            segments.append((line[last_idx:match.start()], False))
        segments.append((match.group(1), True))
        last_idx = match.end()
    if last_idx < len(line):
        segments.append((line[last_idx:], False))
    return segments

# IMPORTANT: Remove the old command-line execution block from the end of your original file:
#
# if __name__ == "__main__":
#     outputFileName = sys.argv[1] if len(sys.argv) > 1 else sys.exit(...)
#     inputfileName = sys.argv[2] if len(sys.argv) > 2 else sys.exit(...)
#     markdown_content = ""
#     with open(inputfileName, "r") as f:
#         markdown_content = f.read()
#     create_pdf(markdown_content, outputFileName)
#     print(f"PDF '{outputFileName}' created successfully.")