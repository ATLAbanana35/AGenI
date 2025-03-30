# Installation Guide for StoryAI

## This is a Windows-Only documentation, Linux users know how to convert the commands (I actually wrote this code on Arch Linux btw)

This guide provides step-by-step instructions to manually install and set up the StoryAI application without running the provided `install_run.py` script.

---

## Prerequisites

1. **Python Installation**  
   Ensure you have Python 3.8 or later installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. **Pip Installation**  
   Verify that `pip` is installed by running the following command in your terminal:
   ```bash
   python -m ensurepip --upgrade
   ```
   If it says "command not found" -> Go here [Add python to path](https://realpython.com/add-python-to-path/).
   If this fails, install `pip` manually by following the instructions on the [pip documentation](https://pip.pypa.io/en/stable/installation/).

---

## Step 1: Install Dependencies

1. Upgrade `pip` to the latest version:
   ```bash
   python -m pip install --upgrade pip
   ```
2. Install the required Python packages:
   ```bash
   python -m pip install pillow requests websocket-client websockets gradio
   ```

---

## Step 2: Download and Install Additional Tools

### Ollama
1. Visit the [Ollama download page](https://ollama.com/download/windows).
2. Download and install Ollama on your system.

### ComfyUI
1. Visit the [ComfyUI download page](https://download.comfy.org/windows/nsis/x64).
2. Download and install ComfyUI.
3. **For AMD GPU Users**: Follow the [AMD-specific installation tutorial](https://www.youtube.com/watch?v=RtSNtwjHuYQ).

---

## Step 3: Download the Models Files

### Text-To-Image:
1. Visit the [model download page](https://civitai.com/models/827184/wai-nsfw-illustrious-sdxl).
2. Download the `wai-nsfw-illustrious-sdxl` model file.
3. Move the downloaded file to the following directory:
   ```
   [ComfyUI installation folder]/models/checkpoints/
   ```

### Text-to-Text:
4. Run the model using the following command (in powershell):
    ```bash
    ollama run mannix/llama3.1-8b-abliterated
    ```


---

## Step 4: Create a `run.bat` File

1. Open a text editor and paste the following content:
   ```batch
   @echo off
   tasklist | findstr /I "ollama.exe" >nul
   if %errorlevel% neq 0 (
       start /B ollama serve
       timeout /t 5
   )

   msg * "Post-Installation: Enable ComfyUI API: Go on settings (the gear icon) search Dev Mode, enable it, and restart ComfyUI"

   python app.py
   ```
2. Save the file as `run.bat` in the root directory of your application.

---

## Step 5: Final Steps

1. Create a file named `installed.txt` in the root directory of your application and add the text `Installed` to it.
2. Run the application by double-clicking the `run.bat` file.

---

## Notes

- **ComfyUI API Configuration**: After launching ComfyUI, enable the API by navigating to the settings (gear icon), searching for "Dev Mode," enabling it, and restarting ComfyUI.
- **Virtual Environment Activation**: Always activate the virtual environment before running the application.

---

Congratulations! You have successfully installed and set up StoryAI. If you encounter any issues, refer to the documentation or seek support from the community.


Similar code found with 1 license type