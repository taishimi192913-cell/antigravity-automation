import os
import json
from duckduckgo_search import DDGS
from openai import OpenAI
from datetime import datetime

def main():
    print("🚀 [Step 1/3] Starting automated research...")
    
    # 1. DuckDuckGoで最新トレンドの検索 (YouTubeやWebの話題の代わり)
    try:
        ddgs = DDGS()
        # 話題のアニメ、AI技術、またはVTuber関連のニュースを検索
        topic = "AI VTuber technology trends Japan OR Virtual YouTuber news"
        print(f"🔍 Searching for: {topic}")
        results = list(ddgs.text(topic, max_results=5))
        
        research_text = ""
        for r in results:
            research_text += f"- {r['title']}: {r['body']}\n"
    except Exception as e:
        print("⚠️ Error during DuckDuckGo search:", e)
        research_text = "No recent data available."

    print("📄 Research data gathered:")
    print(research_text)

    # 2. OpenAIにリサーチ結果を渡してAI VTuber用の台本やネタを生成
    print("\n🧠 [Step 2/3] Generating VTuber script with OpenAI...")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY is not set. Please set it in GitHub Secrets.")
        return

    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    あなたはAI VTuber（メンヘラ系、名前はサクラ）のプロデューサー兼構成作家です。
    以下の最新のWebリサーチ結果をもとに、サクラが今日のショート動画で話すための
    「フリートークの台本」を生成してください。

    リサーチ結果:
    {research_text}
    
    【サクラのキャラクター設定】
    ・視聴者のことが大好きで少し依存気味。
    ・最新テクノロジーやネットニュースにも興味があるが、最終的には「私のことだけ見てほしい」と結びつける。
    
    出力形式は以下のJSONでお願いします:
    {{
      "title": "動画のタイトル (YouTube Shorts用)",
      "hook": "視聴者を惹きつける最初の1文",
      "script": "サクラのセリフ（句読点を含め100文字〜150文字程度）",
      "emotion": "Happy / Sad / Angry / Neutral のいずれか"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        result_json = response.choices[0].message.content
        data = json.loads(result_json)
        
        print("\n✨ === Generated VTuber Script ===")
        print(f"📌 Title  : {data.get('title')}")
        print(f"🪝 Hook   : {data.get('hook')}")
        print(f"🥺 Emotion: {data.get('emotion')}")
        print(f"💬 Script : {data.get('script')}")
        
        # 3. 結果をファイルに保存する（将来的にRemotionで動画化するため）
        print("\n💾 [Step 3/3] Saving result...")
        os.makedirs("output", exist_ok=True)
        today = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/vtuber_script_{today}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Script saved to {output_file}")
        
    except Exception as e:
        print("❌ Error during OpenAI generation:", e)

if __name__ == "__main__":
    main()
