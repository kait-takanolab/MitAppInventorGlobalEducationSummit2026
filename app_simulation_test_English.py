import os
import io

from flask import Flask, request, render_template
from flask_cors import CORS
import numpy as np
from PIL import Image
from keras.preprocessing.image import img_to_array
from google import genai

app = Flask(__name__)
CORS(app)

# Prease write your Gemini-APIkey↓
client = genai.Client(api_key="(Gemini-APIkey)")

@app.route('/',methods = ['GET'])
def top():
    return render_template("Blockly_simulation_hyouzi_English.html")

@app.route('/simulation', methods=['POST'])
def save_image():
    if 'image' not in request.files:
        return "サーバーにファイルが届いていません", 400

    try:
        #シミュレーション用ブロック画像の取得
        file = request.files['image']
        img = Image.open(file.stream)
        user_img = img.convert('RGB')
        
        #お手本画像の選択、取得
        topic = request.form.get('topic')
        model_img_name = f"./image/{topic}_1.png"
        print(model_img_name)
        
        #お手本の画像の取得
        model_img = Image.open(model_img_name)

        # プロンプトの構成
        prompt = [
            "1枚目がお手本の画像、2枚目がユーザーが作成した画像です。",
            "お手本の画像は日本語で、ユーザーが作成した画像は英語で記載されています。",
            "これから、ユーザーに対して、1枚目の画像に近づくように、2枚目のフローのどこに問題があるのかを指摘してもらいます。",
            "このプログラムをそのまま実行した時に、2枚目のフローで起こり得るシチュエーション（問題点または成功シナリオ）を考えてください。",
            "【重要】出力は、以下のルールとフォーマットに従って、必ず「1〜3」の3つの項目で構成してください。",
            "これらの文章は、英語に翻訳して出力してください。日本語の原文は必要ありません。",

            
            "＜出力の構成ルール＞",
            "・もしも赤いブロック（フロータイトル）がお手本画像と意味が大きく異なる場合(言語が違う場合を除いて)、ユーザーがトピック設定を間違えている可能性があります。その場合は、以下の指示を全て無視して、「トピックの設定が間違っているかも！タイトルを見直してみよう。」とだけ返してください。",
            "・不測の状況（問題点）が3つある場合は、3つすべて問題点を指摘してください。",
            "・問題点が3つもない（0〜2個しかない）場合は、無理に問題点を作らず、残りの項目は「プログラムが上手くいったシミュレーション（成功シナリオ）」で埋めて、合計が必ず3項目になるようにしてください。",
            "・問題点が0個（完璧にできている）の場合は、3つの項目すべてを「成功シナリオ」にしてください。また、その場合はリストの前後に「とてもよくできています！」といった褒め言葉を添えてください。",
            
            "＜出力フォーマット＞",
            "1.[1つ目のシチュエーション]",
            "2.[2つ目のシチュエーション]",
            "3.[3つ目のシチュエーション]",
            
            "＜出力の例（※お題が自動販売機の場合の例です。実際は画像の内容に合わせたシチュエーションにしてください）＞"
            "＜出力の例（問題点が0個・完璧な場合）＞",
            "とてもよくできています！このプログラムなら、こんな風にバッチリ動くよ！",
            "1.お金を入れたら、ボタンがピカピカ光ったよ！（※成功シナリオ）",
            "2.ジュースが買えたよ！（※成功シナリオ）",
            "3.お釣りも回収できたよ！（※成功シナリオ）",
            "※出力時は、末尾の（※成功シナリオ）といった注釈は含めず、セリフのみを出力してください。",
            
            "＜絶対の禁止事項＞",
            "・「〇〇のブロックを消して」「〇〇のブロックを上に動かして」といった、具体的なブロックの変更アドバイスや修正手順は絶対に書かないでください。子供が自分で気づけるように、何が起きるか（状況）だけを伝えてください。",
            
            "＜その他のルール＞",
            "・小学校3年生向けの文章で、簡潔で分かり易い表現を使用してください。",
            "・「不測の状況（問題点）」というのは、ユーザが作成したフローを忠実に実行した故の問題点のことです。そもそも機械が故障しているなど、ユーザーのフローとは関係のない問題は考慮しないでください。",
            "・お手本は完成形です。ユーザーに対して、お手本に書かれている以上の指摘はしないでください。", 
            "・もしもユーザーが、適切かつお手本画像以上に詳細なブロック画像を作成した場合は、より詳細にされたり追加された箇所については問題点としないでください。", 
            
            model_img, # お手本
            user_img   # ユーザー提出
        ]

        print("Geminiが考え中です...")

        # 回答生成
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print(response.text)

        return response.text
    
    except Exception as e:
        return f"error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)