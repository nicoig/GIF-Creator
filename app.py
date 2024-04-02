# Para crear el requirements.txt ejecutamos 
# pipreqs --encoding=utf8 --force

# Primera Carga a Github
# git init
# git add .
# git remote add origin https://github.com/nicoig/GIF-Creator.git
# git commit -m "Initial commit"
# git push -u origin master

# Actualizar Repo de Github
# git add .
# git commit -m "Se actualizan las variables de entorno"
# git push origin master

# En Render
# agregar en variables de entorno
# PYTHON_VERSION = 3.9.12

################################################



import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile
import os

def calculate_crop_size(source_width, source_height, target_width, target_height):
    """Calcula el tamaño y la posición del recorte para mantener la relación de aspecto."""
    source_aspect = source_width / source_height
    target_aspect = target_width / target_height

    if source_aspect > target_aspect:
        # El video es más ancho que el objetivo: recortar a lo ancho
        crop_height = source_height
        crop_width = int(crop_height * target_aspect)
    else:
        # El video es más alto que el objetivo: recortar a lo alto
        crop_width = source_width
        crop_height = int(crop_width / target_aspect)

    x_center = source_width / 2
    y_center = source_height / 2

    crop_x_start = max(0, int(x_center - crop_width / 2))
    crop_y_start = max(0, int(y_center - crop_height / 2))

    return (crop_x_start, crop_y_start, crop_x_start + crop_width, crop_y_start + crop_height)

def main():
    st.title("Creador de GIF")

    uploaded_video = st.file_uploader("Sube un video para convertirlo en GIF", type=["mp4", "mov", "avi", "mpeg", "mkv", "mpg", "mpeg4"])

    if uploaded_video is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='_' + uploaded_video.name) as tfile:
            tfile.write(uploaded_video.read())
            video_path = tfile.name

        video_clip = VideoFileClip(video_path)
        video_duration = int(video_clip.duration)
        original_width, original_height = video_clip.size

        st.write(f"Tamaño original del video: {original_width} x {original_height} px")

        target_width = st.number_input("Ancho objetivo (px)", min_value=1, value=original_width, max_value=original_width)
        target_height = st.number_input("Alto objetivo (px)", min_value=1, value=original_height, max_value=original_height)

        # Lógica para sliders de duración basada en la duración del video
        if video_duration < 60:  # Menos de un minuto
            start_time = st.slider("Inicio del GIF (segundos)", 0, video_duration, 0)
            end_time = st.slider("Fin del GIF (segundos)", 0, video_duration, video_duration)
        else:  # Un minuto o más
            max_minutes = video_duration // 60
            start_minutes = st.slider("Inicio del GIF (minutos)", 0, max_minutes, 0)
            start_seconds = st.slider("Inicio del GIF (segundos adicionales)", 0, 59, 0)
            end_minutes = st.slider("Fin del GIF (minutos)", 0, max_minutes, max_minutes)
            end_seconds = st.slider("Fin del GIF (segundos adicionales)", 0, 59, 0)
            start_time = start_minutes * 60 + start_seconds
            end_time = end_minutes * 60 + end_seconds

        if st.button("Crear GIF"):
            if start_time < end_time:
                crop_box = calculate_crop_size(original_width, original_height, target_width, target_height)
                cropped_clip = video_clip.subclip(start_time, end_time).crop(x1=crop_box[0], y1=crop_box[1], x2=crop_box[2], y2=crop_box[3])
                output_gif_name = os.path.splitext(uploaded_video.name)[0] + ".gif"
                output_gif_path = os.path.join(tempfile.gettempdir(), output_gif_name)
                cropped_clip.write_gif(output_gif_path, fps=10, program='ffmpeg')

                st.success("¡GIF creado exitosamente!")
                st.image(output_gif_path)

                with open(output_gif_path, "rb") as file:
                    st.download_button(label="Descargar GIF", data=file, file_name=output_gif_name, mime="image/gif")
            else:
                st.error("El tiempo de inicio debe ser menor que el tiempo de fin.")

        video_clip.close()
        os.unlink(video_path)

if __name__ == "__main__":
    main()

