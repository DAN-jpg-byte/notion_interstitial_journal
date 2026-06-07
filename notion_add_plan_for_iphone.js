
/**
 * こちらはスラッシュを入れると改行するバージョンになってます！（※URL欄は除く）
 * 【Notion PLAN・タスク追加 for iOS】
 * * 概要:
 * iPhoneからNotionのPLAN用データベースへ、タスクを素早く登録するためのScriptableスクリプト。
 * * 主な機能:
 * 1. iOS標準のAlert UIを用いた「PLAN名・目的・関連URL」の入力
 * 2. Notion API (v1/pages) へのPOST送信（Python版 notion_add_plan.py と同一プロパティ）
 * 3. 「いつやるか？」は送信日の JST（YYYY-MM-DD）を自動設定
 * 4. 送信完了後、iOS URL Scheme (shortcuts://) を利用して自動的にホーム画面へ帰還
 * * 依存関係:
 * - iOS ショートカット: 「GoHome」という名前の「ホーム画面へ移動」アクションを含むショートカットが必要
 * * 作成日: 2026-05-14
 */

/**
 * 【Notion PLAN・タスク追加 for iOS】
 * * Python版 notion_add_plan.py のScriptable移植版です。
 * 音声入力の「スラッシュ」改行は PLAN名・目的のみ（URLは https:// 等に / が含まれるため未適用）
 */

// --- 🔽 ここをあなたの情報に書き換えてください 🔽 ---
const NOTION_API_TOKEN = "あなたのAPIトークンをここに";
const DATABASE_ID = "あなたのPLAN用データベースIDをここに"; // .env の PLAN_DATABASE_ID と同じ
// -----------------------------------------------------

const NOTION_API_URL = "https://api.notion.com/v1/pages";

function slashToNewline(s) {
  return s.replace(/スラッシュ|\/|／/g, "\n");
}

async function run() {
  let alert = new Alert();
  alert.title = "Notion Quick Add";
  alert.message = "PLAN・タスクを入力してください";

  // 入力フィールド（Python版と同じ並び）
  alert.addTextField("■ PLAN・タスク名", ""); // 0
  alert.addTextField("■ 目的", ""); // 1
  alert.addTextField("■ 関連URL", ""); // 2

  alert.addAction("Notionに登録");
  alert.addCancelAction("キャンセル");

  let responseIndex = await alert.presentAlert();

  if (responseIndex === -1) return;

  let titleText = slashToNewline(alert.textFieldValue(0)).trim();
  let goalText = slashToNewline(alert.textFieldValue(1)).trim();
  let urlText = alert.textFieldValue(2).trim();

  if (!titleText) {
    let errAlert = new Alert();
    errAlert.title = "入力エラー";
    errAlert.message = "名前（PLAN・タスク名）は必須です。";
    await errAlert.present();
    return;
  }

  // JST の今日（YYYY-MM-DD）— Python版と同様
  let currentDate = new Date().toLocaleDateString("en-CA", {
    timeZone: "Asia/Tokyo",
  });

  let body = {
    parent: { database_id: DATABASE_ID },
    properties: {
      title: {
        title: [{ text: { content: titleText } }],
      },
      "%3DVzQ": {
        rich_text: [{ text: { content: goalText } }],
      },
      "%5DrhS": {
        url: urlText || null,
      },
      "RV%40e": {
        date: { start: currentDate },
      },
    },
  };

  let req = new Request(NOTION_API_URL);
  req.method = "POST";
  req.headers = {
    Authorization: `Bearer ${NOTION_API_TOKEN}`,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
  };
  req.body = JSON.stringify(body);

  try {
    let res = await req.loadJSON();
    if (req.response.statusCode === 200) {
      let n = new Notification();
      n.title = "送信成功";
      n.body = "NotionにPLANを登録しました。";
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
