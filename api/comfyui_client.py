import json
import uuid
import websocket
import asyncio
import urllib.request

class ComfyUIClient:
    def __init__(self, server_address="127.0.0.1:8188"):
        """
        Initialize the ComfyUI client with the server address.
        """
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

    def queue_prompt(self, prompt):
        """
        Send a prompt to the ComfyUI API queue.
        """
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_images(self, prompt):
        """
        Connect to the WebSocket API and retrieve generated images.
        """
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(self.server_address, self.client_id))
        prompt_id = self.queue_prompt(prompt)["prompt_id"]
        output_images = {}
        current_node = ""

        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message["type"] == "executing":
                    data = message["data"]
                    if data["prompt_id"] == prompt_id:
                        if data["node"] is None:
                            break  # Execution is done
                        else:
                            current_node = data["node"]
            else:
                if current_node == "save_image_websocket_node":
                    images_output = output_images.get(current_node, [])
                    images_output.append(out[8:])  # Extract image bytes
                    output_images[current_node] = images_output

        ws.close()
        return output_images

    def generate_image(self, positive_prompt, negative_prompt, seed=5, steps=20, cfg=8, width=512, height=512):
        """
        Generate an image using the ComfyUI API with the specified parameters.
        Returns the image bytes directly.
        """
        # Define the default workflow
        prompt = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": cfg,
                    "denoise": 1,
                    "latent_image": ["5", 0],
                    "model": ["4", 0],
                    "negative": ["7", 0],
                    "positive": ["6", 0],
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "seed": seed,
                    "steps": steps,
                },
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "waiNSFWIllustrious_v120.safetensors",
                },
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "batch_size": 1,
                    "height": height,
                    "width": width,
                },
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": positive_prompt,
                },
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": negative_prompt,
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2],
                },
            },
            "save_image_websocket_node": {
                "class_type": "SaveImageWebsocket",
                "inputs": {
                    "images": ["8", 0],
                },
            },
        }

        # Retrieve images via WebSocket
        images = self.get_images(prompt)
        return images


# Usage Example
if __name__ == "__main__":
    from PIL import Image
    import io

    # Initialize the client
    client = ComfyUIClient()

    # Define prompts
    positive_prompt = "masterpiece best quality girl"
    negative_prompt = "bad hands"

    # Generate an image
    try:
        images = client.generate_image(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            seed=12345,
            steps=30,
            cfg=7,
            width=768,
            height=768,
        )

        # Display the first image
        for node_id in images:
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                image.show()

    except Exception as e:
        print("Error:", e)