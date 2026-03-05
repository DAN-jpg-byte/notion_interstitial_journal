
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
 *「目的」項目を含めて記録するスクリプト
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

  // 入力フィールドの追加（Python版と同じ並びにしています）
  alert.addTextField("終わったこと・完了したこと", ""); // 0
  alert.addTextField("始めたこと・次にやりたいこと", ""); // 1
  alert.addTextField("目的 ＆ 目標時間(何時までか？)", "");                     // 2 (追加)
  alert.addTextField("気持ち", "");                   // 3
  alert.addTextField("後でやりたいこと、メモなど", "");    // 4

  alert.addAction("Notionに送信");
  alert.addCancelAction("キャンセル");

  let responseIndex = await alert.presentAlert();
 
  if (responseIndex === -1) return; 

  // 各項目の取得と改行処理（「スラッシュ」の置換）
  let doneText = alert.textFieldValue(0).replace(/スラッシュ|\/|／/g, '\n');
  let nextText = alert.textFieldValue(1).replace(/スラッシュ|\/|／/g, '\n');
  let goalText = alert.textFieldValue(2).replace(/スラッシュ|\/|／/g, '\n'); // 追加
  let moodText = alert.textFieldValue(3).replace(/スラッシュ|\/|／/g, '\n');
  let memoText = alert.textFieldValue(4).replace(/スラッシュ|\/|／/g, '\n');

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
      // 「目的」のID: qTOI を追加
      "qTOI": {
        "rich_text": [{ "text": { "content": goalText } }]
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
      n.body = "Notionに目的を含めて記録しました。";
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
// ホーム画面に戻る（ショートカット "GoHome" が必要です）
Safari.open("shortcuts://run-shortcut?name=GoHome");
Script.complete();