# ComfyUI-Blender Feature Additions Summary

## Overview
This document details the features and enhancements added to the ComfyUI-Blender integration, including viewport preview rendering, deferred render execution, and fixed filename output support.

---

## 1. Viewport Preview Rendering

### Purpose
Enable users to capture viewport previews (OpenGL renders) directly from Blender as input for ComfyUI workflows, complementing the existing camera render capability.

### Implementation

**New File: `comfyui_blender/operators/render_viewport_preview.py`**
- Operator class: `COMFY_OT_RenderViewportPreview`
- Uses `bpy.ops.render.opengl()` for viewport capture
- Follows same pattern as existing render operators
- Supports "Update on Run" scheduling (see feature #2)
- Key methods:
  - `execute()`: Handles scheduling logic when "Update on Run" is enabled
  - `_execute_render()`: Performs actual viewport rendering

**Modified: `comfyui_blender/__init__.py`**
- Added registration for new `RenderViewportPreview` operator

**Modified: `comfyui_blender/panels/input_panel.py`**
- Added "Viewport Preview" button to image input nodes
- Button appears alongside existing "Render View" button
- Shows checkmark and depressed state when scheduled

---

## 2. Update on Run Feature

### Purpose
Allow users to defer render execution until workflow submission. When enabled, clicking render buttons schedules the renders instead of executing immediately. All scheduled renders execute automatically when the workflow is run.

### Key Behavior
- **Sticky Scheduling**: Scheduled renders persist across multiple workflow runs until manually disabled
- **Visual Feedback**: Scheduled buttons show checkmark icon and depressed appearance
- **Single Toggle**: One "Update on Run" toggle controls all render types

### Implementation

**Modified: `comfyui_blender/settings.py`**

Added `ScheduledRenderPropertyGroup`:
```python
class ScheduledRenderPropertyGroup(bpy.types.PropertyGroup):
    workflow_property: StringProperty()  # Which input node property
    render_type: EnumProperty(items=[
        ("render_view", "Render View", ""),
        ("render_viewport_preview", "Render Viewport Preview", ""),
        ("render_depth_map", "Render Depth Map", ""),
        ("render_lineart", "Render Lineart", "")
    ])
```

Added to `ComfyUIAddonPreferences`:
- `update_on_run`: BoolProperty with toggle callback
- `scheduled_renders`: CollectionProperty to track scheduled renders
- `executing_scheduled_renders`: Guard flag to prevent callback interference

Toggle callback implementation:
```python
def update_on_run_toggle(self, context):
    if hasattr(self, 'executing_scheduled_renders') and self.executing_scheduled_renders:
        return  # Don't clear during execution
    if not self.update_on_run:
        self.scheduled_renders.clear()  # Clear when disabled
```

**Modified: `comfyui_blender/operators/run_workflow.py`**

Added scheduled render execution before workflow submission:
```python
# Execute all scheduled renders
addon_prefs.executing_scheduled_renders = True
addon_prefs.update_on_run = False  # Temporarily disable

try:
    for scheduled_render in scheduled_list:
        workflow_property = scheduled_render.workflow_property
        render_type = scheduled_render.render_type

        # Execute appropriate render operator
        if render_type == "render_view":
            bpy.ops.comfy.render_view('EXEC_DEFAULT', workflow_property=workflow_property)
        elif render_type == "render_viewport_preview":
            bpy.ops.comfy.render_viewport_preview('EXEC_DEFAULT', workflow_property=workflow_property)
        # ... etc for other render types

    # Don't clear scheduled_renders - keep sticky behavior
finally:
    addon_prefs.update_on_run = original_update_on_run
    addon_prefs.executing_scheduled_renders = False
```

**Modified: All 4 Render Operators**
Files modified:
- `comfyui_blender/operators/render_view.py`
- `comfyui_blender/operators/render_viewport_preview.py`
- `comfyui_blender/operators/render_depth_map.py`
- `comfyui_blender/operators/render_lineart.py`

Pattern applied to each:
```python
def execute(self, context):
    addon_prefs = context.preferences.addons[__package__.split('.')[0]].preferences

    if addon_prefs.update_on_run:
        # Schedule the render instead of executing
        # First, remove any existing scheduled render for this property
        for i, scheduled in enumerate(addon_prefs.scheduled_renders):
            if scheduled.workflow_property == self.workflow_property:
                addon_prefs.scheduled_renders.remove(i)
                break

        # Add new scheduled render
        new_render = addon_prefs.scheduled_renders.add()
        new_render.workflow_property = self.workflow_property
        new_render.render_type = "render_viewport_preview"  # Specific to each operator

        return {'FINISHED'}

    # Otherwise execute immediately
    return self._execute_render(context)

def _execute_render(self, context):
    # Original render execution logic
    ...
```

**Modified: `comfyui_blender/panels/input_panel.py`**

Added UI toggle:
```python
row = layout.row()
row.prop(addon_prefs, "update_on_run", text="Update on Run", icon="TIME")
```

Updated button rendering to show scheduled state:
```python
# Check if this render type is scheduled
scheduled_render_type = None
for scheduled in addon_prefs.scheduled_renders:
    if scheduled.workflow_property == workflow_property:
        scheduled_render_type = scheduled.render_type
        break

# Show checkmark and depressed state for scheduled renders
if scheduled_render_type == "render_viewport_preview":
    render_viewport = row.operator("comfy.render_viewport_preview",
                                   text="", icon="CHECKMARK", depress=True)
else:
    render_viewport = row.operator("comfy.render_viewport_preview",
                                   text="", icon="RESTRICT_RENDER_OFF")
```

### Bug Fixes
1. **Scheduled renders clearing after workflow run**: Added `executing_scheduled_renders` guard flag to prevent the toggle callback from clearing scheduled renders during execution
2. **Callback interference**: Used guard flag pattern to safely disable/re-enable toggle without triggering unwanted clears

---

## 3. Fixed Filename Feature

### Purpose
Allow ComfyUI workflows to output images with fixed, non-incrementing filenames. This enables:
- Overwriting the same output file each run
- Direct file references in Blender that always point to latest output
- Automatic image reload in Blender's image viewer

### ComfyUI Server Side Implementation

**Modified: `nodes/blender_output_save_image.py`**

Added optional `fixed_filename` input:
```python
@classmethod
def INPUT_TYPES(cls):
    INPUT_TYPES = super().INPUT_TYPES()
    INPUT_TYPES["optional"] = INPUT_TYPES.get("optional", {})
    INPUT_TYPES["optional"]["fixed_filename"] = (IO.STRING, {"default": ""})
    return INPUT_TYPES
```

Implemented dual-save logic:
```python
def save_images(self, images, filename_prefix="blender", prompt=None, extra_pnginfo=None, fixed_filename=""):
    # Call parent to handle normal incrementing save
    result = super().save_images(images, filename_prefix, prompt, extra_pnginfo)

    # If fixed_filename provided, also save to that location
    if fixed_filename and fixed_filename.strip():
        # Get last saved file info
        last_saved = result["ui"]["images"][-1]
        source_filename = last_saved["filename"]
        source_subfolder = last_saved.get("subfolder", "")

        # Build paths
        source_path = os.path.join(output_dir, source_subfolder, source_filename)
        safe_fixed_filename = os.path.basename(fixed_filename.strip())

        # Ensure .png extension
        if not safe_fixed_filename.lower().endswith('.png'):
            safe_fixed_filename += '.png'

        fixed_path = os.path.join(output_dir, safe_fixed_filename)

        # Copy to fixed filename (overwrites if exists)
        shutil.copy2(source_path, fixed_path)

        # Add fixed filename to result for Blender import
        fixed_image_info = {
            "filename": safe_fixed_filename,
            "subfolder": source_subfolder,
            "type": "output"
        }
        result["ui"]["images"].append(fixed_image_info)

    return result
```

### Blender Add-on Side Implementation

**Modified: `comfyui_blender/connection.py`**

Added filename detection logic:
```python
# Detect fixed vs incrementing filenames
# Incrementing files match pattern: prefix_NNNNN_.ext (e.g., "blender_00001_.png")
# Fixed files don't have the trailing underscore after digits
filename_no_ext = os.path.splitext(output["filename"])[0]
is_incrementing = bool(re.search(r'_\d+_$', filename_no_ext))
is_fixed_filename = not is_incrementing
```

Implemented fixed filename download (bypassing auto-increment):
```python
if is_fixed_filename:
    # Download directly to overwrite existing file
    outputs_folder = get_outputs_folder()
    subfolder_path = os.path.join(outputs_folder, output.get("subfolder", ""))
    os.makedirs(subfolder_path, exist_ok=True)
    filepath = os.path.join(subfolder_path, output["filename"])

    # Build download URL
    params = {
        "filename": output["filename"],
        "subfolder": output["subfolder"],
        "type": output.get("type", "output"),
        "rand": os.urandom(8).hex()
    }
    url = get_server_url("/view", params=params)

    # Download and overwrite
    response = requests.get(url, params=params, headers=headers, stream=True)
    if response.status_code == 200:
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    filename = output["filename"]
else:
    # For incrementing files, use normal download (auto-increments)
    filename, filepath = download_file(output["filename"], output["subfolder"], output.get("type", "output"))
```

Implemented image reload and viewer refresh:
```python
def add_image_output(output=output, filename=filename, filepath=filepath, is_fixed=is_fixed_filename):
    image_object = None

    if is_fixed:
        # For fixed filenames, reload existing image if it exists
        # Blender stores images with full filename including extension
        if filename in bpy.data.images:
            image_object = bpy.data.images[filename]
            image_object.reload()

            # Force update of any image editors displaying this image
            for screen in bpy.data.screens:
                for area in screen.areas:
                    if area.type == 'IMAGE_EDITOR':
                        for space in area.spaces:
                            if space.type == 'IMAGE_EDITOR':
                                if space.image and space.image.name == filename:
                                    # Force viewer refresh by reassigning
                                    temp_img = space.image
                                    space.image = None
                                    space.image = temp_img
                                    area.tag_redraw()

    # If not found or not fixed, load as new
    if not image_object:
        image_object = bpy.data.images.load(filepath, check_existing=True)
        image_object.preview_ensure()

    # Add to outputs collection if not already there
    existing_output = None
    for existing in outputs_collection:
        if existing.name == image_object.name and existing.type == "image":
            existing_output = existing
            break

    if not existing_output:
        image = outputs_collection.add()
        image.name = image_object.name
        image.filepath = os.path.join(output["subfolder"], filename)
        image.type = "image"

    # Refresh image editor UI
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.tag_redraw()
```

### Bug Fixes Throughout Development

1. **Fixed filenames not imported to Blender**
   - Root cause: Fixed filename not included in result data
   - Fix: Added fixed filename to `result["ui"]["images"]` array

2. **Fixed filenames incrementing in Blender** (e.g., Primary_fixed_1.png)
   - Root cause 1: Incorrect detection logic treating all files as fixed
   - Fix: Changed to regex pattern `r'_\d+_$'` for proper detection
   - Root cause 2: `get_filepath()` and `bpy.data.images.load()` auto-incrementing
   - Fix: Bypass normal download path, use direct download with overwrite

3. **Image viewer not reloading**
   - Root cause: Looking for image without extension but Blender stores with extension
   - Evidence: Logs showed looking for "Primary_fixed" but Blender had "Primary_fixed.png"
   - Fix: Changed from `os.path.splitext(filename)[0]` to using full `filename`

4. **Viewer not visually refreshing**
   - Root cause: `reload()` updates data but doesn't refresh UI
   - Fix: Added viewer refresh logic (reassign image to force UI update)

---

## Technical Patterns Used

### Guard Flag Pattern
Used in "Update on Run" feature to prevent callback interference:
```python
try:
    addon_prefs.executing_scheduled_renders = True
    # Do work that would normally trigger callback
finally:
    addon_prefs.executing_scheduled_renders = False
```

### Dual Save Pattern
Used in fixed filename feature to maintain both incrementing and fixed outputs:
1. Call parent `save_images()` for normal incrementing save
2. Copy result to fixed filename location
3. Add both to result data

### Regex-based Detection
Used to distinguish file types without false positives:
```python
# Matches "prefix_00001_" but not "prefix_fixed" or "prefix_custom"
is_incrementing = bool(re.search(r'_\d+_$', filename_no_ext))
```

### Main Thread Execution Pattern
All Blender data modifications executed via timer on main thread:
```python
def add_image_output(...):
    # Blender API calls here

bpy.app.timers.register(add_image_output)
```

---

## Files Modified Summary

### New Files Created
- `comfyui_blender/operators/render_viewport_preview.py`

### ComfyUI Server Side
- `nodes/blender_output_save_image.py`

### Blender Add-on Side
- `comfyui_blender/__init__.py`
- `comfyui_blender/settings.py`
- `comfyui_blender/connection.py`
- `comfyui_blender/panels/input_panel.py`
- `comfyui_blender/operators/run_workflow.py`
- `comfyui_blender/operators/render_view.py`
- `comfyui_blender/operators/render_depth_map.py`
- `comfyui_blender/operators/render_lineart.py`

---

## Usage Examples

### Using Viewport Preview
1. In Blender, navigate to ComfyUI panel
2. Set up viewport as desired
3. Click "Viewport Preview" button on any image input node
4. Image is rendered and sent to ComfyUI workflow

### Using Update on Run
1. Enable "Update on Run" toggle at top of panel
2. Click render buttons to schedule (they show checkmark icon)
3. Adjust scene/settings as needed
4. Click "Run Workflow" - all scheduled renders execute, then workflow runs
5. Scheduled renders remain active for next workflow run (sticky)
6. Disable toggle to clear all scheduled renders

### Using Fixed Filename
1. In ComfyUI workflow, add `BlenderOutputSaveImage` node
2. Set `filename_prefix` as usual (e.g., "Primary")
3. Set `fixed_filename` to desired name (e.g., "Primary_fixed")
4. Run workflow multiple times
5. Both files saved:
   - `Primary_00001_.png`, `Primary_00002_.png`, ... (incrementing)
   - `Primary_fixed.png` (overwrites each time)
6. In Blender, `Primary_fixed.png` automatically reloads in image viewer

---

## Benefits

### Viewport Preview Rendering
- Quick visual feedback without full camera render
- Useful for material previews, pose checking, composition tests
- Faster iteration cycles

### Update on Run
- Batch multiple renders before workflow execution
- Reduce manual clicking when iterating
- Maintain consistent render schedule across iterations
- Clear visual feedback of what will render

### Fixed Filename
- Stable file references in Blender
- No need to manually update image references
- Automatic viewer refresh shows latest output
- Cleaner output folder (one reference file instead of hundreds)
- Useful for iterative workflows where only latest result matters

---

## Commit History

1. Initial viewport preview implementation
2. Added Update on Run feature
3. Fixed scheduled renders clearing bug
4. Added fixed filename support to BlenderOutputSaveImage
5. Fixed filename detection and import logic
6. Fixed image viewer reload functionality
7. Removed verbose debugging output

---

*Generated: 2026-01-19*
