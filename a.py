from PIL import Image

def place_letters_on_template(template_path, letters_folder, output_path):
    # Load the template
    template = Image.open(template_path)

    # Dimensions of each cell (you might need to adjust these)
    cell_width, cell_height = 140, 140  # Example dimensions

    # Starting positions of the first cell (you might need to adjust these)
    start_x, start_y = 290, 290  # Example starting positions

    # Load and place each letter image
    for i in range(26):  # Assuming only uppercase letters A-Z
        char = chr(ord('A') + i)
        image_filename = f"char_{i}.png"  # Construct filename based on index

        try:
            # Load the letter image
            letter_image = Image.open(f"{letters_folder}/{image_filename}")
            letter_image = letter_image.resize((cell_width, cell_height))

            # Calculate position based on the custom layout
            if i < 4:  # First line (A, B, C, D)
                x = start_x + (i % 4) * (cell_width )
                y = start_y
            elif i < 12:  # Second line (E, F, G, H, I, J, K, L)
                x = start_x-290 + ((i - 4) % 8) * (cell_width)
                y = start_y + (cell_height + 40)
            elif i < 20:  # Third line (M, N, O, P, Q, R, S, T)
                x = start_x-290 + ((i - 12) % 8) * (cell_width )
                y = start_y + 2 * (cell_height + 40)
            else:  # Fourth line (U, V, W, X, Y, Z)
                x = start_x-290 + ((i - 20) % 6) * (cell_width )
                y = start_y + 3 * (cell_height + 40)

            # Paste the letter image onto the template
            template.paste(letter_image, (x, y))
        except FileNotFoundError:
            print(f"No image for {char}")

    # Save the modified template
    template.save(output_path)

# Example usage
place_letters_on_template("WhatsApp Image 2024-06-18 at 12.56.32 PM.jpeg", "PngNew", "output_template.png")
