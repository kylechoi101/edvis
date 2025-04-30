from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

title_font =ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 100)
text_font =ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 50)

# Load the wildfire image (background) and the graph image
wildfire_img = Image.open("wildfire.png").convert("RGBA")
graph_img = Image.open("plot.png").convert("RGBA")

# Resize the graph image to fit the width of the wildfire image
graph_resized = graph_img.resize((wildfire_img.width, 500))

# Make the graph semi-transparent
graph_overlay = Image.new("RGBA", graph_resized.size)
graph_overlay = Image.alpha_composite(graph_overlay, graph_resized)
graph_overlay.putalpha(180)  # adjust transparency (0-255)

# Paste the semi-transparent graph onto the wildfire image (at bottom)
combined_img = wildfire_img.copy()
combined_img.paste(graph_overlay, (0, 300), graph_overlay)
draw = ImageDraw.Draw(combined_img)
title_text1 = "Blank "
title_text2 = "Bond"

# 중앙 위치 계산
title_width = draw.textlength(title_text1 + title_text2, font=title_font)
title_x = (combined_img.width - title_width) // 2
title_y = 40

# "Blank"는 검은색, "Bond"는 초록색
draw.text((title_x, title_y), title_text1, font=title_font, fill="white")
draw.text((title_x + draw.textlength(title_text1, font=title_font), title_y),
          title_text2, font=title_font, fill="green")


# Display the result
plt.figure(figsize=(10, 10))
plt.imshow(combined_img)
plt.axis('off')
combined_img.save("final_output.png")
plt.show()
