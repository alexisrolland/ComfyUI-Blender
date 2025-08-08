# ComfyUI Blender Add-on

This folder contains the source code of the Blender add-on.

## Dependencies

The Blender add-on dependencies are bundled in the `_vendor/` folder using Vendorize as suggested by the [official Blender documentation](https://docs.blender.org/manual/en/latest/advanced/extensions/addons.html).

To update dependencies:

- Update the file `vendorize.toml` to add or update packages.
- Run Vendorize as below to automatically download dependencies in the `_vendor/` folder.

```sh
python -m venv .venv
source .venv/bin/activate

# Install and run Vendorize
python -m pip install vendorize
python-vendorize
```