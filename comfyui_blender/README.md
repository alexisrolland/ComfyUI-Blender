# ComfyUI Blender

This folder contains the source code of the Blender add-on.

#### Dependencies:

Blender plugin dependencies are bundled in the project as suggested from [the doc](https://docs.blender.org/manual/en/latest/advanced/extensions/addons.html).  

To updated it just re-run the vendorize:  

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install vendorize
python-vendorize
```

dependencies will then be automatically bundled with the plugin.  
