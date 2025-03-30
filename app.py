import gradio as gr
from api.comfyui_client import ComfyUIClient
from api.ollama_client import OllamaClient
from prompts import llm_sd_prompt_generator, llm_generate_character, llm_sd_prompt_generator_v2
from PIL import Image
import io
import random
import json
import os
import webbrowser
import threading
import time


# Initialize clients
ollama_client = OllamaClient(model="mannix/llama3.1-8b-abliterated")
comfy_client = ComfyUIClient()

# Ensure JSON files exist
for fname in ["characters.json", "scenes.json"]:
    if not os.path.exists(fname):
        with open(fname, "w") as f:
            json.dump({}, f)
    else:
        try:
            with open(fname, "r") as f:
                json.load(f)  # Attempt to load the JSON to ensure it's valid
        except json.JSONDecodeError:
            with open(fname, "w") as f:
                json.dump({}, f)  # Reset to an empty JSON if invalid

def load_json_data(filename):
    with open(filename, "r") as f:
        return json.load(f)

def save_json_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

async def generate_character(character_name, character_description):
    try:
        prompt = llm_sd_prompt_generator.format(PROMPT=character_description)
        response = ollama_client.generate_response(llm_generate_character.format(PROMPT=prompt))
        
        # Load, update, and save characters
        characters = load_json_data("characters.json")
        characters[character_name] = response
        save_json_data("characters.json", characters)
        def thread():
            time.sleep(3)
            os._exit(0)
        thread = threading.Thread(target=thread)
        thread.start()
        return (
            f"FOR TECHNICAL REASONS, YOU'LL NEED TO RELOAD THE WEBPAGE AND RESTART THE APPLICATION!\nCharacter '{character_name}' created successfully!\n\nDescription:\n{response}"
        )
    except Exception as e:
        return f"Error: {str(e)}", *[gr.update()] * 3  # Return unchanged components on error
def update_character_prompt(character_name, new_prompt):
    characters = load_json_data("characters.json")
    if character_name not in characters:
        return f"Character '{character_name}' not found."
    
    characters[character_name] = new_prompt
    save_json_data("characters.json", characters)
    return f"Prompt for '{character_name}' updated successfully!"

def update_scene_prompt(scene_name, new_prompt):
    scenes = load_json_data("scenes.json")
    if scene_name not in scenes:
        return f"Scene '{scene_name}' not found."
    
    scenes[scene_name] = new_prompt
    save_json_data("scenes.json", scenes)
    return f"Prompt for '{scene_name}' updated successfully!"

async def generate_scene(scene_name, scene_description):
    try:
        prompt = llm_sd_prompt_generator.format(PROMPT=scene_description)
        response = ollama_client.generate_response(llm_generate_character.format(PROMPT=prompt))
        
        # Load, update, and save scenes
        scenes = load_json_data("scenes.json")
        scenes[scene_name] = response
        save_json_data("scenes.json", scenes)
        def thread():
            time.sleep(3)
            os._exit(0)
        thread = threading.Thread(target=thread)
        thread.start()
        return (
            f"FOR TECHNICAL REASONS, YOU'LL NEED TO RELOAD THE WEBPAGE AND RESTART THE APPLICATION!\nScene '{scene_name}' created successfully!\n\nDescription:\n{response}"
        )
    except Exception as e:
        return f"Error: {str(e)}", *[gr.update()] * 3  # Return unchanged components on error

async def generate_image_from_prompt(prompt):
    positive_prompt = ollama_client.generate_response(llm_sd_prompt_generator.format(PROMPT=prompt))
    negative_prompt = "bad quality,worst quality,worst detail,sketch,censor, bad hands, bad face"
    
    images = comfy_client.generate_image(
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        seed=random.randint(0, 100000),
        steps=30,
        cfg=7,
        width=1024,
        height=512,
    )
    
    for node_id in images:
        for image_data in images[node_id]:
            return Image.open(io.BytesIO(image_data))
    return None

async def generate_image_v1(character_name, additional_prompt, environment):
    characters = load_json_data("characters.json")
    if character_name not in characters:
        return None, "Character not found"
    
    full_prompt = f"Character: {characters[character_name]}, {additional_prompt}, environment: {environment}"
    image = await generate_image_from_prompt(full_prompt)
    return image, "Image generated successfully"

async def generate_image_v2(character_name, scene_name, image_type,character_position, character_action, 
                          camera_angle, afar_view, lighting, mood, clothing, additional_prompt):
    width = 1024 if image_type == "Landscape" else 512
    height = 512 if image_type == "Landscape" else 1024
    characters = load_json_data("characters.json")
    scenes = load_json_data("scenes.json")
    
    if character_name not in characters:
        return None, "Character not found"
    if scene_name not in scenes:
        return None, "Scene not found"
    
    prompt = llm_sd_prompt_generator_v2.format(
        POSITION=character_position,
        ACTION=character_action,
        CAMERA_ANGLE=camera_angle,
        AFAR_VIEW=afar_view,
        CLOTHES=clothing,
        APPEARANCE=characters[character_name],
        ENVIRONMENT=scenes[scene_name],
        LIGHTING=lighting,
        MOOD=mood,
        PROMPT=additional_prompt+", the name of the character is: "+character_name
    )
    
    positive_prompt = ollama_client.generate_response(prompt)
    negative_prompt = "bad quality,worst quality,worst detail,sketch,censor, bad hands, bad face"
    
    images = comfy_client.generate_image(
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        seed=random.randint(0, 100000),
        steps=30,
        cfg=7,
        width=width,
        height=height,
    )
    
    for node_id in images:
        for image_data in images[node_id]:
            return Image.open(io.BytesIO(image_data)), "Image generated successfully; prompt: "+prompt
    return None, "Generation failed"

# Character prompt editor
def character_prompt_editor(character_name):
    characters = load_json_data("characters.json")
    if character_name not in characters:
        return f"Character '{character_name}' not found."

    current_prompt = characters[character_name]
    with gr.Blocks() as editor:
        gr.Markdown(f"### Editing Prompt for Character: {character_name}")
        prompt_editor = gr.Textbox(
            label="Edit Character Prompt",
            value=current_prompt,
            lines=5
        )
        save_button = gr.Button("Save Changes")
        status_output = gr.Textbox(label="Status", interactive=False)

        def save_changes(new_prompt):
            characters[character_name] = new_prompt
            save_json_data("characters.json", characters)
            return f"Prompt for '{character_name}' updated successfully!"

        save_button.click(
            lambda new_prompt: save_changes(new_prompt),
            inputs=prompt_editor,
            outputs=status_output
        )

    return editor
def load_scene_prompt(name):
    scenes = load_json_data("scenes.json")
    return scenes.get(name, "")
def load_character_prompt(name):
    characters = load_json_data("characters.json")
    return characters.get(name, "")
# Scene prompt editor
def scene_prompt_editor(scene_name):
    scenes = load_json_data("scenes.json")
    if scene_name not in scenes:
        return f"Scene '{scene_name}' not found."
    current_prompt = scenes[scene_name]
    with gr.Blocks() as editor:
        gr.Markdown(f"### Editing Prompt for Scene: {scene_name}")
        prompt_editor = gr.Textbox(
            label="Edit Scene Prompt",
            value=current_prompt,
            lines=5
        )
        save_button = gr.Button("Save Changes")
        status_output = gr.Textbox(label="Status", interactive=False)
        def save_changes(new_prompt):
            scenes[scene_name] = new_prompt
            save_json_data("scenes.json", scenes)
            return f"Prompt for '{scene_name}' updated successfully!"
        save_button.click(
            lambda new_prompt: save_changes(new_prompt),
            inputs=prompt_editor,
            outputs=status_output
        )
    return editor

with gr.Blocks(title="Character & Image Generator") as app:
    gr.Markdown("# 🎭 Character & Image Generation System")
    with gr.Tab("Create Character"):
        with gr.Row():
            char_name = gr.Textbox(label="Character Name")
            char_desc = gr.Textbox(label="Character Description", lines=3)
        char_submit = gr.Button("Generate Character")
        char_output = gr.Textbox(label="Result", interactive=False)
    
    with gr.Tab("Create Scene"):
        with gr.Row():
            scene_name = gr.Textbox(label="Scene Name")
            scene_desc = gr.Textbox(label="Scene Description", lines=3)
        scene_submit = gr.Button("Generate Scene")
        scene_output = gr.Textbox(label="Result", interactive=False)
    with gr.Tab("Edit Character Prompt"):
        char_name = gr.Dropdown(label="Select Character", choices=list(load_json_data("characters.json").keys()))
        char_prompt = gr.Textbox(label="Character Prompt", lines=5)
        char_save = gr.Button("Save Changes")
        char_status = gr.Textbox(label="Status", interactive=False)
        
        # Load character prompt when selection changes
        char_name.change(fn=load_character_prompt, inputs=char_name, outputs=char_prompt)
        
        # Save changes when button is clicked
        char_save.click(fn=update_character_prompt, inputs=[char_name, char_prompt], outputs=char_status)
    
    # Scene Prompt Editor
    with gr.Tab("Edit Scene Prompt"):
        scene_name = gr.Dropdown(label="Select Scene", choices=list(load_json_data("scenes.json").keys()))
        scene_prompt = gr.Textbox(label="Scene Prompt", lines=5)
        scene_save = gr.Button("Save Changes")
        scene_status = gr.Textbox(label="Status", interactive=False)
        
        # Load scene prompt when selection changes
        scene_name.change(fn=load_scene_prompt, inputs=scene_name, outputs=scene_prompt)
        
        # Save changes when button is clicked
        scene_save.click(fn=update_scene_prompt, inputs=[scene_name, scene_prompt], outputs=scene_status)

    with gr.Tab("Generate Image (Simple)"):
        image_prompt = gr.Textbox(label="Prompt", lines=3)
        image_submit = gr.Button("Generate Image")
        image_output = gr.Image(label="Generated Image")
    
    with gr.Tab("Generate Image (V1 - Character)"):
        with gr.Row():
            v1_char = gr.Dropdown(
                label="Select Character", 
                choices=list(load_json_data("characters.json").keys())
            )
            v1_prompt = gr.Textbox(label="Additional Prompt")
            v1_env = gr.Textbox(label="Environment")
        v1_submit = gr.Button("Generate Image")
        v1_image = gr.Image(label="Generated Image")
        v1_output = gr.Textbox(label="Status", interactive=False)
    
    with gr.Tab("Generate Image (V2 - Advanced)"):
        with gr.Row():
            v2_char = gr.Dropdown(
                label="Character", 
                choices=list(load_json_data("characters.json").keys())
            )
            v2_scene = gr.Dropdown(
                label="Scene", 
                choices=list(load_json_data("scenes.json").keys())
            )
            v3_type = gr.Dropdown(
                label="Type", 
                choices=["Landscape", "Portrait"]
            )
        with gr.Row():
            v2_pos = gr.Textbox(label="Character Position", placeholder="e.g. lying down, standing up")
            v2_action = gr.Textbox(label="Character Action", placeholder="e.g. sleeping, running")
        with gr.Row():
            v2_angle = gr.Textbox(label="Camera Angle", placeholder="e.g. top view, left view")
            v2_view = gr.Textbox(label="View Distance", placeholder="e.g. close-up, afar, full body")
        with gr.Row():
            v2_light = gr.Textbox(label="Lighting", placeholder="e.g. red light, evening light")
            v2_mood = gr.Textbox(label="Mood", placeholder="e.g. happy, sad")
        v2_clothes = gr.Textbox(label="Clothing", placeholder="e.g. dress, suit, naked ;-)")
        v2_prompt = gr.Textbox(label="Additional Prompt", placeholder="Correction of the image (e.g. Add a book in her hands)")
        v2_submit = gr.Button("Generate Image")
        v2_image = gr.Image(label="Generated Image")
        v2_output = gr.Textbox(label="Status", interactive=False)
    
    # Event handlers
    char_submit.click(
        generate_character,
        inputs=[char_name, char_desc],
        outputs=char_output
    )
    
    scene_submit.click(
        generate_scene,
        inputs=[scene_name, scene_desc],
        outputs=scene_output
    )
    
    image_submit.click(
        generate_image_from_prompt,
        inputs=image_prompt,
        outputs=image_output
    )
    
    v1_submit.click(
        generate_image_v1,
        inputs=[v1_char, v1_prompt, v1_env],
        outputs=[v1_image, v1_output]
    )
    
    v2_submit.click(
        generate_image_v2,
        inputs=[v2_char, v2_scene, v3_type, v2_pos, v2_action, v2_angle, v2_view, v2_light, v2_mood, v2_clothes, v2_prompt],
        outputs=[v2_image, v2_output]
    )
    
    # Refresh dropdowns when JSON changes
    def refresh_dropdowns():
        characters = list(load_json_data("characters.json").keys())
        scenes = list(load_json_data("scenes.json").keys())
        return characters, characters, scenes
    
    app.load(
        fn=refresh_dropdowns,
        outputs=[v1_char, v2_char, v2_scene]
    )

# app.launch(server_port=8080) # Local usage
# app.launch(share=True) # For sharing
webbrowser.open("http://localhost:8085") # Open in browser
app.launch(server_name="0.0.0.0", server_port=8085) # For remote usage