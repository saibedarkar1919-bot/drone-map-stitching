import cv2
import os
import tkinter as tk
from tkinter import filedialog
import datetime

def stitch_bulk_images(image_folder):
    print(f"Scanning folder: {image_folder}")
    
    # 1. BULLETPROOF FILE FINDER
    image_paths = []
    valid_extensions = ('.jpg', '.jpeg', '.png')
    
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(valid_extensions):
            full_path = os.path.join(image_folder, filename)
            image_paths.append(full_path)
    
    if len(image_paths) < 2:
        print(f"\nCRITICAL ERROR: Could not find enough images.")
        return
        
    print(f"SUCCESS! Found {len(image_paths)} images. Loading them into memory...")
    
    images = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            images.append(img)
            
    if len(images) < 2:
        print("Error: Not enough valid images loaded. Exiting.")
        return

    print("Starting the stitching process. This might take a minute...")
    
    # Updated to the standard, cross-compatible OpenCV 4+ method
    stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA) 
    
    status, stitched_panorama = stitcher.stitch(images)
    
    if status == cv2.Stitcher_OK:
        print("\nSuccess! The images were stitched perfectly.")
        
        # Get the current local date and time
        now = datetime.datetime.now()
        
        # Format it: Year-Month-Day_Hour-Minute-Second
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create the new dynamic filename
        filename = f"mapstitching_{timestamp}.jpg"
        
        # Save the file
        output_path = os.path.join(image_folder, filename)
        cv2.imwrite(output_path, stitched_panorama)
        print(f"Saved output map to: {output_path}")
        
        h, w = stitched_panorama.shape[:2]
        if w > 1600:
            scale = 1600 / w
            display_img = cv2.resize(stitched_panorama, (int(w * scale), int(h * scale)))
        else:
            display_img = stitched_panorama
            
        cv2.imshow("Bulk Stitched Map (Resized for Viewing)", display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("\n--- Stitching failed! ---")
        if status == cv2.Stitcher_ERR_NEED_MORE_IMGS:
            print("Reason: Not enough overlapping features between the images.")
        elif status == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
            print("Reason: Failed to calculate the perspective shift (Homography).")
        elif status == cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL:
            print("Reason: Failed to adjust the camera parameters globally.")

# --- Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    
    print("Opening file explorer... Please select your image folder.")
    TARGET_FOLDER = filedialog.askdirectory(title="Select Folder with Images to Stitch")
    
    # Properly close out the background Tkinter instance
    root.destroy()
    
    if TARGET_FOLDER:
        TARGET_FOLDER = os.path.normpath(TARGET_FOLDER)
        stitch_bulk_images(TARGET_FOLDER)
    else:
        print("No folder selected. Exiting script.")