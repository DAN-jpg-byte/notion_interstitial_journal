
# 📱 iPhoneからNotionへ爆速メモ！自動ジャーナリング・システム

iPhoneのホーム画面からパッと入力画面を開き、Notionのデータベースに「今の状態やメモ」を素早く送信できる仕組みです。
アプリが立ち上がりっぱなしにならず、**入力が終わったら自動でホーム画面に戻る**ため、作業の集中力を途切れさせません。

プログラミングの知識がない方でも、この手順通りに進めれば15分程度でセットアップできます！

---

## 🛠️ 準備するもの

設定を始める前に、以下の3つを用意してください。

1. **Notionのアカウント**と、記録用のデータベース（表）
2. **「Scriptable」アプリ**（App Storeで無料でダウンロードできます）
3. **「ショートカット」アプリ**（iPhoneに最初から入っている標準アプリです）

---

## 🚀 設定手順（ステップ・バイ・ステップ）

### ステップ1：Notionと連携するための「鍵」を手に入れる

まずは、ScriptableがあなたのNotionにデータを書き込めるようにするための「APIトークン（専用のパスワードのようなもの）」を取得します。

1. パソコンやブラウザから [Notionのインテグレーション設定ページ](https://www.notion.so/my-integrations) にアクセスします。
2. **「新しいインテグレーション」** をクリックし、名前に「iPhoneメモ用」などと入力して保存します。
3. 発行された **「シークレット（APIトークン）」** をコピーして、どこかにメモしておきます。（※後で使います）

### ステップ2：Notionのデータベースを設定する

次に、先ほど作った「鍵」が、あなたのデータベースを使えるように許可を出します。

1. 記録したいNotionのデータベースのページを開きます。
2. 画面右上の **「・・・」** アイコンをクリックし、**「コネクト（Connections）」** を選びます。
3. 検索窓にステップ1でつけた名前（例：iPhoneメモ用）を入力し、追加して連携を許可します。
4. そのデータベースのURLを見て、**データベースID** をコピーしてメモします。
* URLが `https://www.notion.so/abcdefg1234567?v=...` の場合、`abcdefg1234567` の部分がIDです。



### ステップ3：iPhoneを自動でホーム画面に戻す準備

入力が終わった後に、iPhoneが自動でホーム画面に戻るための「裏技」をセットします。

1. iPhoneの **「ショートカット」** アプリを開きます。
2. 右上の **「＋」** ボタンを押して、新しいショートカットを作ります。
3. 画面下の検索窓で「ホーム画面」と検索し、**「ホーム画面へ移動」** というアクションを追加します。
4. 画面上のタイトル部分をタップし、名前を **`GoHome`** に変更して「完了」を押します。（※必ず半角英数字で `GoHome` にしてください）

### ステップ4：Scriptableにコードを貼り付ける

いよいよ、メインの仕組みを作ります。

1. iPhoneで **「Scriptable」** アプリを開きます。
2. 右上の **「＋」** ボタンを押して、新しいスクリプトを作成します。
3. 以下のコードをすべてコピーして、画面に貼り付けます。
4. コードの上の方にある `"あなたのAPIトークン"` と `"あなたのデータベースID"` の部分を、ステップ1と2でメモしたものに書き換えます（ダブルクォーテーション `"` は消さないように注意してください）。
5. 左上のタイトルをタップし、名前に `NotionJournal` などとつけて保存します。

```javascript
/**
 * 【Notion Interstitial Journaling for iOS】
 * iPhoneからNotionへ素早く記録し、自動でホーム画面に戻るスクリプトです。
 */

// --- 🔽 ここをあなたの情報に書き換えてください 🔽 ---
const NOTION_API_TOKEN = "あなたのAPIトークン";
const DATABASE_ID = "あなたのデータベースID";
// ----------------------------------------------------

const NOTION_API_URL = "https://api.notion.com/v1/pages";

async function run() {
  let alert = new Alert();
  alert.title = "今の状態を記録";
  
  // 入力項目
  alert.addTextField("完了したこと (Title)", "");
  alert.addTextField("次にやりたいこと", "");
  alert.addTextField("気持ち", "");
  alert.addTextField("後でやりたいこと、メモなど", "");

  alert.addAction("Notionに送信");
  alert.addCancelAction("キャンセル");

  let responseIndex = await alert.presentAlert();
  if (responseIndex === -1) return; 

  let doneText = alert.textFieldValue(0);
  let nextText = alert.textFieldValue(1);
  let moodText = alert.textFieldValue(2);
  let memoText = alert.textFieldValue(3);
  let currentTime = new Date().toISOString();

  // Notionへ送るデータの形（※ご自身のデータベースのプロパティIDに合わせて調整してください）
  let body = {
    "parent": { "database_id": DATABASE_ID },
    "properties": {
      "title": { "title": [{ "text": { "content": doneText } }] },
      "I%5BJp": { "date": { "start": currentTime } },
      "udPY": { "rich_text": [{ "text": { "content": nextText } }] },
      "cNJ%5C": { "rich_text": [{ "text": { "content": moodText } }] },
      "c%3BQ%7C": { "rich_text": [{ "text": { "content": memoText } }] }
    }
  };

  let req = new Request(NOTION_API_URL);
  req.method = "POST";
  req.headers = {
    "Authorization": `Bearer ${NOTION_API_TOKEN}`,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
  };
  req.body = JSON.stringify(body);

  try {
    let res = await req.loadJSON();
    if (req.response.statusCode === 200) {
      // 成功時は静かに終了します
    } else {
      throw new Error(`エラー: ${req.response.statusCode}\n${JSON.stringify(res)}`);
    }
  } catch (e) {
    let errAlert = new Alert();
    errAlert.title = "送信エラー";
    errAlert.message = e.toString();
    await errAlert.present();
  }
}

// 処理を実行し、終わったらステップ3で作った「GoHome」を呼び出してホーム画面に戻る
await run();
Safari.open("shortcuts://run-shortcut?name=GoHome");
Script.complete();

```

### ステップ5：起動用のショートカットを作る（完成！）

最後に、このスクリプトをワンタップで呼び出すボタンを作ります。

1. 再度 **「ショートカット」** アプリを開き、右上の「＋」で新規作成します。
2. 検索窓で「Scriptable」を検索し、**「Run Script」** を選びます。
3. 青い文字の「Script」をタップし、ステップ4で作った `NotionJournal` を選びます。
4. **【重要】** スクリプト名の横の「＞」をタップし、**「Appで実行（Run In App）」を「オン（緑色）」** にします。
5. このショートカットに「ジャーナル入力」など好きな名前をつけて完了です！

お疲れ様でした！
このショートカットをホーム画面に追加すれば、いつでも1タップでNotionへの記録ができるようになります。

---

## ❓ よくある質問・トラブルシューティング

* **Q. 「Alerts are not supported in Siri」という赤いエラーが出ます**
* A. ステップ5の「Appで実行（Run In App）」がオフになっている可能性があります。必ずオン（緑色）にしてください。


* **Q. データがNotionに反映されません**
* A. ステップ2の「コネクト（連携）」を忘れているか、APIトークンやデータベースIDの文字列に余計な空白が入っている可能性があります。確認してみてください。



---

