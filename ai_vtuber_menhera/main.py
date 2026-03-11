import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（APIキー等）
load_dotenv()

# OpenAIのクライアント初期化
# 環境変数 OPENAI_API_KEY が設定されている必要があります
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# VOICEVOXがローカルで立ち上がっているマシンのURLとポート（デフォルトは 50021）
VOICEVOX_URL = 'http://127.0.0.1:50021'

# キャラクターの音声ID（8: 春日部つむぎ, 2: 四国めたん, 14: 冥鳴ひまり, 47: ナースロボ＿タイプＴ）
# ※先ほどは「ナースロボ」だったので意図的にロボット音声になっていました。今回は人間らしい可愛い声（8）に変更します。
SPEAKER_ID = 8

def generate_ai_response(prompt_text, user_message):
    """OpenAI APIを使ってプロンプトとコメントから返答を生成する"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 安価で高速なモデル
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AIの思考中にエラーが起きたみたい……許して？: {e}"

def speak_voicevox(text, speaker_id=SPEAKER_ID):
    """VOICEVOX公開API(tts.quest)を使ってテキストを音声ファイル(WAV)に変換し、Macのafplayで再生する"""
    try:
        print("🎵 音声データ取得中... (Web版API)")
        # tts.quest の無料公開APIを使います
        url = "https://api.tts.quest/v3/voicevox/synthesis"
        params = {'text': text, 'speaker': speaker_id}
        
        # 1. APIを叩いて音声ファイルのダウンロード情報を取得
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        
        # 音声のダウンロードURL、または生成待ち用のURLを取得
        audio_url = data.get("wavDownloadUrl") or data.get("mp3DownloadUrl")
        is_ready = False
        
        # 2. 取得したURLから実際の音声ファイルをダウンロード（生成完了まで待機）
        import time
        max_retries = 30
        for i in range(max_retries):
            # まずaudio_urlにアクセスしてみる
            audio_res = requests.get(audio_url)
            if audio_res.status_code == 200:
                is_ready = True
                break
            
            # 404の場合は生成中。ただし何度も叩くと429になるので少し長めに待つ
            time.sleep(2) 
            
        if not is_ready:
            print("[エラー] 音声の生成が完了しませんでした（タイムアウト）。")
            return
            
        # 3. 音声ファイル(ai_voice.wav)として保存
        with open("ai_voice.wav", "wb") as f:
            f.write(audio_res.content)
            
        print("🎵 メンヘラAI 発話中...")
        # Macの標準コマンドでWAVファイルを再生
        os.system("afplay ai_voice.wav") 
        
    except Exception as e:
        print(f"\n[エラー] 音声合成中に問題が発生しました: {e}")

if __name__ == "__main__":
    print("========================================")
    print("🔪 メンヘラAI VTuber システム 起動テスト")
    print("========================================")
    print("終了する場合は 'quit' または 'exit' と入力してください。\n")
    
    # プロンプトの読み込み
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()
        
    while True:
        user_input = input("🗣️ リスナーのコメント (あなた): ")
        if user_input.lower() in ['quit', 'exit']:
            print("……わたしをおいて、どこに行くの？")
            break
            
        if not user_input.strip():
            continue
            
        print("🧠 AI 思考中...")
        # LLMにテキストを渡して回答を得る
        ai_text = generate_ai_response(system_prompt, user_input)
        
        print(f"\n🎀 AIの返答: {ai_text}\n")
        
        # 得られたテキストを読み上げる
        speak_voicevox(ai_text)
