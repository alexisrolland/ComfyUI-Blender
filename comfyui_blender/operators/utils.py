import bpy
import time
import threading
import websocket

# Global variable to manage the WebSocket thread
websocket_thread = None
websocket_running = False

def websocket_listener(server_address, operator):
    """Background WebSocket listener."""
    global websocket_running
    websocket_running = True

    def on_message(ws, message):
        print(f"Received message: {message}")
        # Use bpy.app.timers to safely update Blender properties
        # bpy.app.timers.register(lambda: process_message(message), first_interval=0.1)

    def on_error(ws, error):
        print(f"WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")
        websocket_running = False

    def on_open(ws):
        print("WebSocket connection established")

    ws = websocket.WebSocketApp(
        server_address,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open

    while websocket_running:
        try:
            ws.run_forever()
        except Exception as e:
            operator.report({'ERROR'}, f"WebSocket exception: {e}")
            time.sleep(5)  # Retry after a delay
        finally:
            ws.close()  # Ensure the WebSocket connection is closed

def process_message(message):
    """Safely process WebSocket messages in Blender's main thread."""
    # Example: Update a custom property in Blender
    print(f"Processing message in Blender: {message}")
    # Add your Blender-specific logic here

def start_websocket_listener(server_address, operator):
    """Start the WebSocket listener in a separate thread."""
    global websocket_thread
    if websocket_thread is None or not websocket_thread.is_alive():
        operator.report({'INFO'}, "Connecting to server...")
        websocket_thread = threading.Thread(target=websocket_listener, args=(server_address, operator), daemon=True)
        websocket_thread.start()

        # Update connection status
        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        addon_prefs.server_connection_status = True
        operator.report({'INFO'}, f"Server status: Connected")
    else:
        operator.report({'INFO'}, "Server status is already connected.")

def stop_websocket_listener(operator):
    """Stop the WebSocket listener."""
    global websocket_running, websocket_thread
    operator.report({'INFO'}, "Disconnecting from server...")
    websocket_running = False
    if websocket_thread and websocket_thread.is_alive():
        websocket_thread.join(timeout=1)  # Add a timeout to prevent blocking
    websocket_thread = None  # Reset the thread variable

    # Update connection status
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.server_connection_status = False
    operator.report({'INFO'}, f"Server status: Disconnected")