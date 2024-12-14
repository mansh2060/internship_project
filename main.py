from diffusers import StableDiffusionPipeline
import torch
import os
import sqlite3
from datetime import datetime
from PIL import Image


def setup_database():
    conn = sqlite3.connect("content_generation.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_content (
            user_id TEXT,
            prompt TEXT,
            image_paths TEXT,
            status TEXT,
            generated_at TEXT
        )
    """)
    conn.commit()
    return conn


def generate_images_for_user(user_id, prompts, model_id="dreamlike-art/dreamlike-diffusion-1.0"):
    
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32, use_safetensors=True)
    pipe = pipe.to("cpu")

    
    user_dir = os.path.join("generated_content", user_id)
    os.makedirs(user_dir, exist_ok=True)

    image_paths = []

   
    for prompt in prompts:
        cursor.execute(
            "INSERT INTO generated_content (user_id, prompt, image_paths, status, generated_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, prompt, None, "Processing", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

    
    for prompt in prompts:
        image = pipe(prompt).images[0]
        image_path = os.path.join(user_dir, f"{prompt.replace(' ', '_')}.png")
        image.save(image_path)
        image_paths.append(image_path)


        cursor.execute(
            "UPDATE generated_content SET image_paths = ?, status = ? WHERE user_id = ? AND prompt = ?",
            (image_path, "Completed", user_id, prompt)
        )
        conn.commit()

   
    print(f"User {user_id}: Your content has been generated and saved in {user_dir}.")


def main():
   
    global conn, cursor
    conn = setup_database()
    cursor = conn.cursor()
    user_id = input("Enter your user ID: ")
    prompts = []
    for i in range(5):
        prompt = input(f"Enter prompt {i + 1}: ")
        prompts.append(prompt)
    
    generate_images_for_user(user_id, prompts)
    conn.close()

if __name__ == "__main__":
    main()