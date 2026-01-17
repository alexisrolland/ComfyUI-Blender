from comfy.comfy_types.node_typing import IO
from nodes import SaveImage
import os
import shutil


class BlenderOutputSaveImage(SaveImage):
    """Node used by ComfyUI Blender add-on to capture an image output from a workflow."""
    CATEGORY = "blender"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["filename_prefix"] = (IO.STRING, {"default": "blender"})
        INPUT_TYPES["optional"] = INPUT_TYPES.get("optional", {})
        INPUT_TYPES["optional"]["fixed_filename"] = (IO.STRING, {"default": ""})
        return INPUT_TYPES

    def save_images(self, images, filename_prefix="blender", prompt=None, extra_pnginfo=None, fixed_filename=""):
        """Override save_images to additionally save to fixed filename if provided."""

        print(f"[BlenderOutputSaveImage] save_images called with fixed_filename='{fixed_filename}'")

        # Call parent save_images to handle the normal incrementing save
        result = super().save_images(images, filename_prefix, prompt, extra_pnginfo)
        print(f"[BlenderOutputSaveImage] Parent save_images completed, result keys: {result.keys() if result else 'None'}")

        # If fixed_filename is provided, also save to that location (without incrementing)
        if fixed_filename and fixed_filename.strip():
            print(f"[BlenderOutputSaveImage] Processing fixed_filename: '{fixed_filename.strip()}'")
            try:
                # Get the output directory from parent class
                output_dir = self.output_dir
                print(f"[BlenderOutputSaveImage] Output directory: {output_dir}")

                # Get the last saved file from the result
                if result and "ui" in result and "images" in result["ui"]:
                    last_saved = result["ui"]["images"][-1]
                    source_filename = last_saved["filename"]
                    source_subfolder = last_saved.get("subfolder", "")
                    print(f"[BlenderOutputSaveImage] Source file: {source_filename}, subfolder: {source_subfolder}")

                    # Build source path
                    if source_subfolder:
                        source_path = os.path.join(output_dir, source_subfolder, source_filename)
                    else:
                        source_path = os.path.join(output_dir, source_filename)

                    # Build fixed filename path (in the same output directory)
                    # Remove any path components from fixed_filename for security
                    safe_fixed_filename = os.path.basename(fixed_filename.strip())

                    # Ensure it has a .png extension
                    if not safe_fixed_filename.lower().endswith('.png'):
                        safe_fixed_filename += '.png'

                    fixed_path = os.path.join(output_dir, safe_fixed_filename)
                    print(f"[BlenderOutputSaveImage] Copying from '{source_path}' to '{fixed_path}'")

                    # Copy the saved image to the fixed filename (overwriting if exists)
                    if os.path.exists(source_path):
                        shutil.copy2(source_path, fixed_path)
                        print(f"[BlenderOutputSaveImage] ✓ Successfully saved to fixed filename: {fixed_path}")

                        # Add the fixed filename to the result so Blender will import it
                        fixed_image_info = {
                            "filename": safe_fixed_filename,
                            "subfolder": source_subfolder,
                            "type": "output"
                        }
                        result["ui"]["images"].append(fixed_image_info)
                        print(f"[BlenderOutputSaveImage] ✓ Added fixed filename to result for Blender import: {fixed_image_info}")
                    else:
                        print(f"[BlenderOutputSaveImage] ✗ Source file does not exist: {source_path}")
                else:
                    print(f"[BlenderOutputSaveImage] ✗ Result structure unexpected. Result: {result}")
            except Exception as e:
                import traceback
                print(f"[BlenderOutputSaveImage] ✗ Error saving to fixed filename: {e}")
                print(f"[BlenderOutputSaveImage] Traceback: {traceback.format_exc()}")
        else:
            print(f"[BlenderOutputSaveImage] Skipping fixed_filename (empty or None)")

        return result