
import os
import shutil
import tempfile

import streamlit as st
from gradio_client import Client, handle_file

st.set_page_config(
    page_title="Mon IA Vidéo",
    page_icon="🎬",
    layout="centered",
)

SPACE_ID = "Saravutw/WAN2.2_I2V_LIGHTNING_4-8step_custom"

st.title("🎬 Mon IA Vidéo")
st.write("Transforme une image en vidéo avec un modèle d’IA ouvert.")

image = st.file_uploader(
    "Choisis l’image de départ",
    type=["png", "jpg", "jpeg", "webp"],
)

prompt = st.text_area(
    "Décris le mouvement souhaité",
    placeholder="Exemple : un lion marche dans la savane au coucher du soleil...",
    height=120,
)

duree = st.selectbox("Durée", [3.5, 5.0], format_func=lambda x: f"{x} secondes")

if st.button("🎬 Générer la vidéo", type="primary", use_container_width=True):
    if image is None:
        st.warning("Importe d’abord une image.")
    elif not prompt.strip():
        st.warning("Décris le mouvement que tu souhaites.")
    else:
        temp_path = None
        try:
            suffix = os.path.splitext(image.name)[1] or ".png"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                f.write(image.getvalue())
                temp_path = f.name

            with st.spinner("Connexion au moteur vidéo et génération en cours…"):
                client = Client(SPACE_ID)
                result = client.predict(
                    input_image=handle_file(temp_path),
                    last_image=handle_file(temp_path),
                    prompt=prompt.strip(),
                    duration_seconds=duree,
                    api_name="/generate_video",
                )

            video_result = result[0]
            video_path = (
                video_result.get("path")
                if isinstance(video_result, dict)
                else video_result
            )

            if not video_path or not os.path.isfile(video_path):
                st.error("Le moteur n’a pas renvoyé de fichier vidéo local.")
            else:
                st.success("Vidéo générée !")
                st.video(video_path)

                with open(video_path, "rb") as f:
                    st.download_button(
                        "⬇️ Télécharger la vidéo",
                        data=f.read(),
                        file_name="ma_video.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                    )

        except Exception as e:
            st.error("La génération a échoué.")
            st.code(str(e))

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
