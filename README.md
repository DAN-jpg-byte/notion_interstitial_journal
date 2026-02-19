
# Interstitial Journaling Tool for Notion

Notionの「インタースティシャル・ジャーナリングDB」へ、デスクトップから素早く入力を送るためのGUIアプリケーションです。

## 概要
このツールは、作業の合間に「今終わったこと」「次にすること」「今の気持ち」を記録し、Notionを開く手間を省いて生産性を維持することを目的としています。作業の切り替え時に思考を整理する「インタースティシャル・ジャーナリング」の手法に最適化されています。

## 主な機能
- **直感的なGUI**: Pythonの `tkinter` を使用した、シンプルで軽量な入力ウィンドウ。
- **堅牢なID指定**: Notionのプロパティを名前（文字列）ではなく、内部的な**固定ID**で指定しています。これにより、Notion上で列名（プロパティ名）を自由に変更しても、プログラムを修正することなく動作し続けます。
- **自動タイムスタンプ**: 送信時に日本時間（JST）のISO 8601形式の日時を自動生成し、Notionへ送信します。
- **入力クリア機能**: 送信成功後、各入力フィールドを自動的にクリアし、連続した記録をスムーズにします。

## セットアップ

### 1. 必要ライブラリのインストール
ターミナルで以下のコマンドを実行し、必要なパッケージをインストールしてください。
```bash
pip install requests python-dotenv
2. 環境変数の設定（.env）
公開リポジトリに機密情報を含めないよう、.env ファイルを使用して設定を管理します。
プロジェクトのルートディレクトリに .env ファイルを作成し、以下の項目を設定してください（.gitignore に .env を追加することを推奨します）。

コード スニペット
NOTION_API_TOKEN=your_notion_api_token_here
DATABASE_ID=your_database_id_here
3. プロパティIDの対応（ソースコード内）
本プログラムは、以下のプロパティIDを使用してNotion APIと通信しています。ご自身のデータベース構造に合わせて notion_interstitial_journal.py 内のIDを確認してください。

完了したこと: title

日時: I%5BJp

気持ち: cNJ%5C

次にやりたいこと: udPY

後でやりたいこと、メモなど: c%3BQ%7C

使い方
プログラムを実行します。

Bash
python notion_interstitial_journal.py
ウィンドウが表示されたら、各項目に内容を入力します。

「Notionに送信」ボタンをクリックします。

下部のログ欄に「送信成功！」と表示されれば、Notionへの記録は完了です。

Created with the help of Gemini - Feb 2026# get_notion_db_ids

Notion APIを活用した自作データーベースID取得用プログラムです。


## フォルダ構成
- `NotionのデータベースIDを調べる.py` : DB内の各プロパティ（列）の固有IDを特定するためのツール。
- `.env` : APIトークンやデータベースIDなどの機密情報を管理（Git等には含めない）。

## 習得した技術・工夫点
1. **ライブラリに頼らないAPI操作**
   - 環境による依存関係のトラブル（AttributeError等）を避けるため、Python標準の `urllib` を使用してNotion APIと直接通信する実装を採用しました。
2. **プロパティIDによる指定**
   - Notion側で列名（例：「山田列」→「近藤列」）を変更してもプログラムが壊れないよう、名前ではなく固有ID（`title`, `I%5BJp` 等）を使用して操作する仕組みを導入しました。

## 例）データベースのプロパティID一覧
*現在の「インタースティシャル・ジャーナリングDB」の構成*　　

| 列名 | ID | 型 |
| :--- | :--- | :--- |
| **完了したこと** | `title` | title |
| **日時** | `I%5BJp` | date |
| **気持ち** | `cNJ%5C` | rich_text |
| **次にやりたいこと** | `udPY` | rich_text |
| **後でやりたいこと、メモなど** | `c%3BQ%7C` | rich_text |

## 使用方法
1. `.env` ファイルに `NOTION_API_TOKEN` と `DATABASE_ID` を設定します。
2. `NotionのデータベースIDを調べる.py` を実行して、最新のDB構造を確認します。

---
*Created with the help of Gemini - Feb 2026*