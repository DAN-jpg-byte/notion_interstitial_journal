
/**
 * こちらはスラッシュを入れると改行するバージョンになってます！
 * 【Notion Interstitial Journaling for iOS】
 * * 概要: 
 * iPhoneからNotionのデータベースへ、インタースティシャル・ジャーナリングを
 * 素早く記録するためのScriptableスクリプト。
 * * 主な機能:
 * 1. iOS標準のAlert UIを用いた「4項目(完了したこと、これからやること、感情、あとでやること)」のテキスト入力
 * 2. Notion API (v1/pages) へのPOST送信
 * 3. 送信完了後、iOS URL Scheme (shortcuts://) を利用して自動的にホーム画面へ帰還
 * * 依存関係: 
 * - iOS ショートカット: 「GoHome」という名前の「ホーム画面へ移動」アクションを含むショートカットが必要
 * * 作成日: 2026-02-19
 */




/**
 * 【Notion Interstitial Journaling for iOS】
 * * 概要: 
 * iPhoneからNotionのデータベースへ、インタースティシャル・ジャーナリングを
 * 素早く記録するためのScriptableスクリプト。(音声入力の「スラッシュ」改行対応版)
 */

// --- 🔽 ここをあなたの情報に書き換えてください 🔽 ---
const NOTION_API_TOKEN = "あなたのAPIトークンをここに";
const DATABASE_ID = "あなたのデータベースIDをここに";
// -----------------------------------------------------

const NOTION_API_URL = "https://api.notion.com/v1/pages";

async function run() {
  let alert = new Alert();
  alert.title = "Interstitial Journaling";
  alert.message = "今の状態を入力してください";

  alert.addTextField("完了したこと (Title)", "");
  alert.addTextField("次にやりたいこと・目的", "");
  alert.addTextField("気持ち", "");
  alert.addTextField("後でやりたいこと、メモなど", "");

  alert.addAction("Notionに送信");
  alert.addCancelAction("キャンセル");

  let responseIndex = await alert.presentAlert();
 
  if (responseIndex === -1) return; 

  // 2. 入力値の取得（「スラッシュ」「/」「／」のいずれかを改行に変換）
  let doneText = alert.textFieldValue(0).replace(/スラッシュ|\/|／/g, '\n');
  let nextText = alert.textFieldValue(1).replace(/スラッシュ|\/|／/g, '\n');
  let moodText = alert.textFieldValue(2).replace(/スラッシュ|\/|／/g, '\n');
  let memoText = alert.textFieldValue(3).replace(/スラッシュ|\/|／/g, '\n');

  let currentTime = new Date().toISOString();

  let body = {
    "parent": { "database_id": DATABASE_ID },
    "properties": {
      "title": {
        "title": [{ "text": { "content": doneText } }]
      },
      "I%5BJp": {
        "date": { "start": currentTime }
      },
      "udPY": {
        "rich_text": [{ "text": { "content": nextText } }]
      },
      "cNJ%5C": {
        "rich_text": [{ "text": { "content": moodText } }]
      },
      "c%3BQ%7C": {
        "rich_text": [{ "text": { "content": memoText } }]
      }
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
      let n = new Notification();
      n.title = "送信成功";
      n.body = "Notionにジャーナルを記録しました。";
      n.schedule();
    } else {
      throw new Error(`エラー: ${req.response.statusCode}\n${JSON.stringify(res)}`);
    }
  } catch (e) {
    let errAlert = new Alert();
    errAlert.title = "エラーが発生しました";
    errAlert.message = e.toString();
    await errAlert.present();
  }
}

await run(); 
Safari.open("shortcuts://run-shortcut?name=GoHome");
Script.complete();