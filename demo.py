from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as stc
import base64
import time
import tempfile
from pathlib import Path
from PIL import Image


# OpenAI client (new SDK style)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 初回表示のフラグとページ番号
if "show_intro" not in st.session_state:
    st.session_state.show_intro = True
if "intro_page" not in st.session_state:
    st.session_state.intro_page = 1

# HTMLクリック可能な画像（画像をボタンに見立てる）
def clickable_image(image_path, next_action):
    with open(image_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    image_html = f"""
    <a href="?next={next_action}">
        <img src="data:image/png;base64,{b64}" 
             style="display: block; margin-left: auto; margin-right: auto; width: 100%; max-width: 1800px; border-radius: 20px; cursor: pointer;" />
    </a>
"""
    st.markdown(image_html, unsafe_allow_html=True)

# クエリパラメータを確認
query_params = st.experimental_get_query_params()
next_action = query_params.get("next", [None])[0]

# --- イントロ表示部分 ---
if st.session_state.show_intro:
    if next_action == "page2":
        st.session_state.intro_page = 2
        st.experimental_set_query_params()
    elif next_action == "main":
        st.session_state.show_intro = False
        st.experimental_set_query_params()
        st.experimental_rerun()

    # ページごとの処理
    if st.session_state.intro_page == 1:
        clickable_image("start.png", "page2")  # 1ページ目
        st.stop()
    elif st.session_state.intro_page == 2:
        clickable_image("home.png", "main")   # 2ページ目（クリックで本編）
        st.stop()


st.set_page_config(page_title="マブダチラップバトル", layout="wide")
st.title("🎤 マブダチラップバトル")

# BGM再生
audio_path1 = 'sample_music.mp3'

audio_placeholder = st.empty()
with open(audio_path1, "rb") as file_:
    contents = file_.read()

audio_str = "data:audio/ogg;base64,%s" % (base64.b64encode(contents).decode())
audio_html = f"""
    <audio id="bgm-player" autoplay loop>
        <source src="{audio_str}" type="audio/ogg">
        Your browser does not support the audio element.
    </audio>
    <script>
        const audio = document.getElementById("bgm-player");
        audio.volume = 0.5;
    </script>
"""

audio_placeholder.empty()
time.sleep(0.5)
audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

col1, col_chat, col2 = st.columns([1.0, 2, 1.0])

# 左側
with col1:
    image_hidari = Image.open("hidari_icon.png")
    st.image(image_hidari, caption='', use_column_width=True)
    
    st.header("左のマブダチ")
    left_name = st.text_input("名前（左）", value="", placeholder="林さん")
    left_traits = [
        st.text_input("魅力①（左）", value="", placeholder="清潔感がある"),
        st.text_input("魅力②（左）", value="", placeholder="剣道が強い"),
        st.text_input("魅力③（左）", value="", placeholder="英検二級")
        # st.text_input("魅力①（左）", "清潔感がある"),
        # st.text_input("魅力②（左）", "剣道が強い"),
        # st.text_input("魅力③（左）", "英検二級")
    ]

# 右側
with col2:
    image_migi = Image.open("migi_icon.png")
    st.image(image_migi, caption='', use_column_width=True)
    st.header("右のマブダチ")
    right_name = st.text_input("名前（右）", value="", placeholder="細谷さん")
    right_traits = [
        
        st.text_input("魅力①（右）", value="", placeholder="デザインがうまい"),
        st.text_input("魅力②（右）", value="", placeholder="嘘がうまい"),
        st.text_input("魅力③（右）", value="", placeholder="友達が多い")

        # st.text_input("魅力①（右）", "デザインがうまい"),
        # st.text_input("魅力②（右）", "嘘がうまい"),
        # st.text_input("魅力③（右）", "SFが好き")
    ]

st.markdown("---")

# STARTボタン
with col_chat:
    
    if st.button("🔥 ラップバトル START！",use_container_width=True):
        if not left_name or not right_name or "" in left_traits or "" in right_traits:
            st.warning("⚠️ すべての項目を入力してください！")
            st.stop()
        with st.spinner("ラップバトル中... 🎤💥"):
            prompt = f"""
以下の2人がマブダチラップバトルを行います。
ラップは合計4ターンで、交互に2回ずつ発言してください。

フォーマットは必ず以下の形で出力してください（ラッパーの名前とラップは別行）：

{left_name}
ラップ1（3〜5行）
{right_name}
ラップ2（3〜5行）
{left_name}
ラップ3（3〜5行）
{right_name}
ラップ4（3〜5行）

【バトル参加者】
- {left_name} の魅力: {', '.join(left_traits)}
- {right_name} の魅力: {', '.join(right_traits)}

相手をディスりつつも、ユーモアや個性を出してラップを作成してください。
前振りなどは全く必要なく、上のフォーマットを満たした4つのフローのみを出力してください。
1フローは50文字
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "あなたはラップバトルの司会者です。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=500
            )

            rap_battle = response.choices[0].message.content

            # ラップ部分だけ抽出
            lines = rap_battle.strip().split("\n")
            flows = []
            buffer = []
            for line in lines:
                if line.strip() in [left_name, right_name]:
                    if buffer:
                        flows.append("\n".join(buffer).strip())
                        buffer = []
                else:
                    buffer.append(line)
            if buffer:
                flows.append("\n".join(buffer).strip())
            # 変数に格納
            left_flow_1 = flows[0]
            right_flow_1 = flows[1]
            left_flow_2 = flows[2]
            right_flow_2 = flows[3]
            all_flows = [left_flow_1, right_flow_1, left_flow_2, right_flow_2]


            voice_placeholder = st.empty()

                        # --- 2. 音声生成 ---
            speech_path = Path(f"speech.mp3")
            with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="nova",  # もしくは "coral"
                input="\n".join(all_flows),
                instructions="Speak in a cheerful and positive tone.",
            ) as response:
                response.stream_to_file(speech_path)

            # --- 3. 音声再生 ---
            with open(speech_path, "rb") as file_:
                contents = file_.read()
            voice_str = "data:audio/ogg;base64,%s" % (base64.b64encode(contents).decode())

            voice_html = f"""
                <audio autoplay=True>
                <source src="{voice_str}" type="audio/ogg">
                Your browser does not support the audio element.
                </audio>
            """

            voice_placeholder.markdown(voice_html, unsafe_allow_html=True)

            for idx, flow in enumerate(all_flows):
                # --- 1. テキスト表示 ---
                if idx % 2 == 0:
                    st.image(image_hidari, caption='', width=50)
                else:
                    st.image(image_migi, caption='', width=50)

                st.markdown(f"<p style='font-size: 40px;'>{flow}</p>", unsafe_allow_html=True)
                st.markdown("---")

                time.sleep(13)



            # 勝敗判定
            st.markdown("### 🏆 勝敗判定")

            judge_prompt = f"""
以下のラップバトルの内容を読んで、どちらのラッパーが勝ったかを判断してください。
勝者の名前（{left_name} または {right_name}）と、その理由を簡潔に答えてください。
その際、両方を褒め、両方が優れた人間であることを示してください。

【ラップバトル内容】
{rap_battle}
"""

            judge_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "あなたはラップバトルの審査員です。"},
                    {"role": "user", "content": judge_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            judge_result = judge_response.choices[0].message.content
            st.success(judge_result)
