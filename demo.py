from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as stc
import base64
import time
import tempfile
from pathlib import Path

# OpenAI client (new SDK style)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

# 説明セクション
explain_1, explain_2 = st.columns([1, 1])

with explain_1:
    st.markdown("""
### 📝 マブダチラップバトルとは？

**マブダチラップバトル**は、  
友達の名前と“いいところ”を入力するだけで、  
彼らがラップでバトルを繰り広げるゲームです。
""")

with explain_2:
    st.markdown("""
### 🔥 このゲームの面白さ

- **友達を勝手に戦わせる背徳感とおかしさ**  
- **ラップを通じて、友達の魅力を再発見できる**
""")

st.markdown("---")
st.markdown("ふざけて遊んでるうちに、ちょっと感動する。  \nそんな**友情再発見バトル**を、ぜひどうぞ。")
st.markdown("---")

col1, col_chat, col2 = st.columns([1.0, 2, 1.0])

# 左側
with col1:
    st.header("😎 左のマブダチ")
    left_name = st.text_input("名前（左）", "林さん")
    left_traits = [
        st.text_input("魅力①（左）", "清潔感がある"),
        st.text_input("魅力②（左）", "剣道が強い"),
        st.text_input("魅力③（左）", "英検二級")
    ]

# 右側
with col2:
    st.header("😈 右のマブダチ")
    right_name = st.text_input("名前（右）", "細谷くん")
    right_traits = [
        st.text_input("魅力①（右）", "デザインがうまい"),
        st.text_input("魅力②（右）", "嘘がうまい"),
        st.text_input("魅力③（右）", "SFが好き")
    ]

st.markdown("---")

# STARTボタン
with col_chat:
    if st.button("🔥 ラップバトル START！"):
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
                st.markdown("---")
                st.markdown(f"<p>{flow}</p>", unsafe_allow_html=True)


                time.sleep(10)



            # 勝敗判定
            st.markdown("---")
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
