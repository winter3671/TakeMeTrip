from PIL import Image
import sys

def make_favicon():
    try:
        img = Image.open('public/logo.png').convert('RGBA')
        data = img.getdata()
        # Remove white background
        new_data = [(i[0], i[1], i[2], 0) if (i[0] > 245 and i[1] > 245 and i[2] > 245) else i for i in data]
        img.putdata(new_data)
        
        bbox = img.getbbox()
        if not bbox:
            print("No content found")
            return
            
        left, top, full_right, bottom = bbox
        
        # Find the gap between icon and text
        right = left
        found_icon = False
        for x in range(left, full_right):
            has_pixel = False
            for y in range(top, bottom):
                if img.getpixel((x, y))[3] > 0:
                    has_pixel = True
                    break
            if has_pixel:
                found_icon = True
            elif found_icon:
                right = x
                break
        
        # Crop the icon
        icon = img.crop((left, top, right, bottom))
        
        # Make it square
        w, h = icon.size
        size = max(w, h)
        res = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        res.paste(icon, ((size - w) // 2, (size - h) // 2))
        
        res.save('public/favicon.png')
        print("Favicon created successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    make_favicon()
