from flask import Flask, render_template, request, jsonify
import os
import re
import requests
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__)
SPEAKER_ID = 8 # 春日部つむぎ

# システムプロンプトの読み込み
prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
with open(prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
        
    # OpenAI APIで返答テキストを生成
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=150
        )
        ai_text = response.choices[0].message.content
    except Exception as e:
        return jsonify({"text": f"エラーが起きたみたいですご主人様……許して？: {e}", "audio": None, "emotion": "sad"})
    
    # 感情タグの解析と、声のトーン（VOICEVOXのspeaker_id）の決定
    # 四国めたん（声のスタイルが豊富なキャラクター）を使用します
    emotion_tag = "Neutral"
    speaker_id = 2  # デフォルト（ノーマル）
    
    match = re.match(r'\[(.*?)\]', ai_text)
    if match:
        emotion_tag = match.group(1).lower()
        # テキストからタグを削除
        ai_text = re.sub(r'\[.*?\]', '', ai_text).strip()
    else:
        emotion_tag = "neutral"
        
    # 感情に応じた声のトーンの割り当て（四国めたんのスタイル）
    if 'happy' in emotion_tag:
        speaker_id = 0  # あまあま（甘えた高い声）
    elif 'fun' in emotion_tag:
        speaker_id = 0  # あまあま
    elif 'angry' in emotion_tag:
        speaker_id = 6  # ツンツン（怒ったような硬い声）
    elif 'sad' in emotion_tag:
        speaker_id = 36 # ひそひそ（メンヘラっぽい、囁き声）
    elif 'asmr' in emotion_tag:
        speaker_id = 36 # ひそひそ（ASMR用の囁き声）
    else:
        speaker_id = 2  # ノーマル

    # VOICEVOX公開API (tts.quest) で音声を生成
    url = "https://api.tts.quest/v3/voicevox/synthesis"
    params = {'text': ai_text, 'speaker': speaker_id}
    
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        audio_url = data.get("wavDownloadUrl") or data.get("mp3DownloadUrl")
        
        if audio_url:
            is_ready = False
            for i in range(30): # 最大30回(約60秒)ポーリング
                audio_res = requests.get(audio_url)
                if audio_res.status_code == 200:
                    is_ready = True
                    break
                time.sleep(2)
            
            if is_ready:
                # staticフォルダに音声ファイルを保存してブラウザからアクセス可能にする
                filepath = os.path.join("static", "ai_voice.wav")
                with open(filepath, "wb") as f:
                    f.write(audio_res.content)
                # キャッシュ対策でクエリパラメータに時間を付ける
                return jsonify({"text": ai_text, "audio": f"/static/ai_voice.wav?t={time.time()}", "emotion": emotion_tag})
                
    except Exception as e:
        print(f"音声生成エラー: {e}")
            
    # 音声生成に失敗した場合はテキストだけ返す
    return jsonify({"text": ai_text, "audio": None, "emotion": emotion_tag})

if __name__ == "__main__":
    print("==================================================")
    print("🌐 ローカルWebサーバーを起動しました！")
    print("👉 ブラウザで http://127.0.0.1:5001 にアクセスしてください")
    print("==================================================")
    app.run(debug=True, port=5001, use_reloader=False)
