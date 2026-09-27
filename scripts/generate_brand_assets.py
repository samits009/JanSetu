import os
import shutil
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

def generate_all_brand_assets():
    source_img_path = r"C:\Users\samit\.gemini\antigravity-ide\brain\bc8c5a7f-069d-46ec-a8d3-d9129736cf89\.user_uploaded\media_1790514057146.jpg"
    workspace_root = r"d:\Development Drive\JanSetu"
    
    print(f"Loading master source image from {source_img_path}...")
    orig = Image.open(source_img_path).convert("RGB")
    
    # 1. Master RGBA (1254x1254)
    # The image is an app icon squircle with black background outside the rounded shield.
    # We create an anti-aliased alpha mask so corners outside the squircle are transparent.
    master_1254 = orig.resize((1254, 1254), Image.Resampling.LANCZOS)
    arr_1254 = np.array(master_1254)
    gray_1254 = np.max(arr_1254, axis=-1)
    
    mask = np.zeros_like(gray_1254, dtype=np.uint8)
    mask[gray_1254 > 4] = 255
    # Smooth blur the mask for a soft anti-aliased edge
    mask_img = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(radius=2.0))
    mask_arr = np.array(mask_img)
    
    rgba_master = Image.fromarray(np.dstack([arr_1254, mask_arr]), "RGBA")
    
    # 2. Bridge Icon (Cropped focused icon for tiny displays / favicons)
    # Centered around the golden figures, bridge arch, and sun (x: 212..812, y: 80..680 in 1024 coords)
    bridge_crop = orig.crop((212, 80, 812, 680))
    bridge_icon_512 = bridge_crop.resize((512, 512), Image.Resampling.LANCZOS)
    
    # Web Brand Output Directory
    web_brand_dir = os.path.join(workspace_root, "frontend", "public", "brand")
    os.makedirs(web_brand_dir, exist_ok=True)
    
    # Save jansetu-logo-master.png
    master_path = os.path.join(web_brand_dir, "jansetu-logo-master.png")
    rgba_master.save(master_path, "PNG", optimize=True)
    print(f"Saved: {master_path} (1254x1254 RGBA)")
    
    # Save jansetu-icon.png
    icon_path = os.path.join(web_brand_dir, "jansetu-icon.png")
    bridge_icon_512.save(icon_path, "PNG", optimize=True)
    print(f"Saved: {icon_path} (512x512 PNG)")
    
    # Save Favicons
    fav_16 = bridge_icon_512.resize((16, 16), Image.Resampling.LANCZOS)
    fav_16_path = os.path.join(web_brand_dir, "favicon-16x16.png")
    fav_16.save(fav_16_path, "PNG")
    print(f"Saved: {fav_16_path}")
    
    fav_32 = bridge_icon_512.resize((32, 32), Image.Resampling.LANCZOS)
    fav_32_path = os.path.join(web_brand_dir, "favicon-32x32.png")
    fav_32.save(fav_32_path, "PNG")
    print(f"Saved: {fav_32_path}")
    
    fav_48 = bridge_icon_512.resize((48, 48), Image.Resampling.LANCZOS)
    fav_ico_path = os.path.join(web_brand_dir, "favicon.ico")
    fav_48.save(fav_ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"Saved: {fav_ico_path}")
    
    # Also save favicon.ico to frontend/public/favicon.ico
    public_fav_ico = os.path.join(workspace_root, "frontend", "public", "favicon.ico")
    shutil.copy2(fav_ico_path, public_fav_ico)
    
    # Apple Touch Icon (180x180)
    # The full logo squircle with dark background fits Apple's guidelines perfectly
    apple_touch = rgba_master.resize((180, 180), Image.Resampling.LANCZOS)
    apple_touch_path = os.path.join(web_brand_dir, "apple-touch-icon.png")
    apple_touch.save(apple_touch_path, "PNG", optimize=True)
    print(f"Saved: {apple_touch_path}")
    
    # PWA Icons (192x192, 512x512)
    pwa_192 = rgba_master.resize((192, 192), Image.Resampling.LANCZOS)
    pwa_192_path = os.path.join(web_brand_dir, "icon-192.png")
    pwa_192.save(pwa_192_path, "PNG", optimize=True)
    print(f"Saved: {pwa_192_path}")
    
    pwa_512 = rgba_master.resize((512, 512), Image.Resampling.LANCZOS)
    pwa_512_path = os.path.join(web_brand_dir, "icon-512.png")
    pwa_512.save(pwa_512_path, "PNG", optimize=True)
    print(f"Saved: {pwa_512_path}")
    
    # PWA Maskable Icon (512x512, padded with #060a12 background to prevent launcher clipping)
    maskable = Image.new("RGBA", (512, 512), (6, 10, 18, 255))
    # Paste scaled master at 80% size (410x410) centered
    scaled_master = rgba_master.resize((410, 410), Image.Resampling.LANCZOS)
    maskable.paste(scaled_master, (51, 51), scaled_master)
    maskable_path = os.path.join(web_brand_dir, "icon-maskable-512.png")
    maskable.save(maskable_path, "PNG", optimize=True)
    print(f"Saved: {maskable_path}")
    
    # 3. Flutter Mobile Assets
    flutter_branding_dir = os.path.join(workspace_root, "mobile", "assets", "branding")
    os.makedirs(flutter_branding_dir, exist_ok=True)
    
    flutter_logo_path = os.path.join(flutter_branding_dir, "jansetu-logo.png")
    rgba_master.resize((1024, 1024), Image.Resampling.LANCZOS).save(flutter_logo_path, "PNG", optimize=True)
    print(f"Saved: {flutter_logo_path}")
    
    flutter_icon_path = os.path.join(flutter_branding_dir, "jansetu-icon.png")
    bridge_icon_512.save(flutter_icon_path, "PNG", optimize=True)
    print(f"Saved: {flutter_icon_path}")
    
    # 4. Android Mipmap Launcher Icons
    android_res_dir = os.path.join(workspace_root, "mobile", "android", "app", "src", "main", "res")
    densities = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }
    for folder, size in densities.items():
        folder_path = os.path.join(android_res_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        icon_file = os.path.join(folder_path, "ic_launcher.png")
        rgba_master.resize((size, size), Image.Resampling.LANCZOS).save(icon_file, "PNG")
        print(f"Saved Android launcher icon: {icon_file} ({size}x{size})")
        
    # Android Adaptive Icon Foreground
    # Adaptive icons need 432x432 foreground with safe area in inner 264x264
    drawable_dir = os.path.join(android_res_dir, "drawable")
    os.makedirs(drawable_dir, exist_ok=True)
    adaptive_fg = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
    fg_scaled = rgba_master.resize((280, 280), Image.Resampling.LANCZOS)
    adaptive_fg.paste(fg_scaled, (76, 76), fg_scaled)
    fg_path = os.path.join(drawable_dir, "ic_launcher_foreground.png")
    adaptive_fg.save(fg_path, "PNG")
    print(f"Saved Android adaptive foreground: {fg_path}")
    
    # Android Launch Image
    launch_img = rgba_master.resize((240, 240), Image.Resampling.LANCZOS)
    launch_img_path = os.path.join(drawable_dir, "launch_image.png")
    launch_img.save(launch_img_path, "PNG")
    print(f"Saved Android launch image: {launch_img_path}")
    
    # 5. iOS AppIcon Set
    ios_icon_dir = os.path.join(workspace_root, "mobile", "ios", "Runner", "Assets.xcassets", "AppIcon.appiconset")
    os.makedirs(ios_icon_dir, exist_ok=True)
    
    ios_sizes = {
        "Icon-App-20x20@1x.png": 20,
        "Icon-App-20x20@2x.png": 40,
        "Icon-App-20x20@3x.png": 60,
        "Icon-App-29x29@1x.png": 29,
        "Icon-App-29x29@2x.png": 58,
        "Icon-App-29x29@3x.png": 87,
        "Icon-App-40x40@1x.png": 40,
        "Icon-App-40x40@2x.png": 80,
        "Icon-App-40x40@3x.png": 120,
        "Icon-App-60x60@2x.png": 120,
        "Icon-App-60x60@3x.png": 180,
        "Icon-App-76x76@1x.png": 76,
        "Icon-App-76x76@2x.png": 152,
        "Icon-App-83.5x83.5@2x.png": 167,
        "Icon-App-1024x1024@1x.png": 1024,
    }
    
    for filename, px in ios_sizes.items():
        out_f = os.path.join(ios_icon_dir, filename)
        # iOS AppIcon should have solid background (no transparent outer corners)
        # We paste the squircle onto midnight navy #060A12
        ios_canvas = Image.new("RGB", (px, px), (6, 10, 18))
        scaled = rgba_master.resize((px, px), Image.Resampling.LANCZOS)
        ios_canvas.paste(scaled, (0, 0), scaled)
        ios_canvas.save(out_f, "PNG")
        print(f"Saved iOS icon: {out_f} ({px}x{px})")
        
    # iOS Launch Image
    ios_launch_dir = os.path.join(workspace_root, "mobile", "ios", "Runner", "Assets.xcassets", "LaunchImage.imageset")
    os.makedirs(ios_launch_dir, exist_ok=True)
    
    for fname, size in [("LaunchImage.png", 180), ("LaunchImage@2x.png", 360), ("LaunchImage@3x.png", 540)]:
        out_launch = os.path.join(ios_launch_dir, fname)
        rgba_master.resize((size, size), Image.Resampling.LANCZOS).save(out_launch, "PNG")
        print(f"Saved iOS launch image: {out_launch} ({size}x{size})")

    print("\nAll brand assets successfully generated from single source of truth!")

if __name__ == "__main__":
    generate_all_brand_assets()
