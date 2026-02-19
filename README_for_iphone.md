

## 📌 Project: Notion Interstitial Journaling for iOS

iPhoneからNotionデータベースへ、インタースティシャル・ジャーナリングを爆速で記録するための自動化システムです。PC版（Python/Tkinter）のデータ構造を完全に継承しつつ、iOSネイティブな操作感を実現しています。

### 🛠 構成要素

1. **Scriptable (JavaScript)**: 入力UIの表示とNotion APIとの通信を担当。
2. **iOS Shortcuts**: アプリの起動と、処理完了後の「ホーム画面への自動帰還」を担当。
3. **Notion API**: データベースへのデータ永続化。

### 🚀 セットアップ手順

#### 1. iOSショートカットの準備

以下の2つのショートカットを作成してください。

* **「GoHome」**:
* アクション: 「ホーム画面へ移動」のみ。
* 役割: Scriptableの処理終了後に自動で呼び出され、ホーム画面に戻ります。


* **「Journal入力（任意名）」**:
* アクション: 「Run Script (Scriptable)」
* 設定: **Run In App をオン** に設定。
* 役割: このシステムを起動するメインのトリガー。



#### 2. Scriptableの設定

`NotionJournal.js` （または任意の名）を作成し、提供されたコードを貼り付けます。

* `NOTION_API_TOKEN`: 自身のインテグレーション内部統合トークンを入力。
* `DATABASE_ID`: 対象のNotionデータベースIDを入力。
* 末尾の `Safari.open("shortcuts://run-shortcut?name=GoHome")` が、手順1で作ったショートカット名と一致していることを確認してください。

### 📝 入力項目

Python版のデータベース設計に基づき、以下の項目をNotionに送信します。

* **完了したこと (Title)**: 実施した作業の内容。
* **次にやりたいこと**: 次のブロックで着手する内容。
* **気持ち**: 現在のメンタルステータス。
* **後でやりたいこと、メモなど**: 備忘録やアイデア。

### 🔄 ワークフロー

1. ホーム画面のアイコンをタップ。
2. Scriptableが立ち上がり、入力ダイアログが表示される。
3. 項目を入力し「Notionに送信」をタップ。
4. API通信完了後、自動的にホーム画面にリダイレクトされる（GoHome連携）。

---

### 💡 開発者メモ

このプロジェクトは、元々Python/Tkinterで構築されたデスクトップツールを、モバイル環境（iOS）に最適化したものです。

* **作成日**: 2026年2月19日
* **技術スタック**: JavaScript (Scriptable), Notion API, iOS URL Schemes

