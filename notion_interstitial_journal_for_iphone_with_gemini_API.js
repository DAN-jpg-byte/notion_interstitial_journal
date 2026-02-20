/**
 * 【AI Interstitial Journaling for iOS】
 * 概要:
 * iOSショートカットの「テキストを音声入力」などで取得したテキストを受け取り、
 * Gemini APIで4項目に分類後、Notionへ自動記録するスクリプト。
 */

// --- 🔽 設定 🔽 ---
const NOTION_API_TOKEN = "あなたのNotion_API_TOKEN";
const DATABASE_ID = "あなたのNotion_DATABASE_ID";
const GEMINI_API_KEY = "あなたのGEMINI_API_KEY";
// -------------------

const NOTION_API_URL = "https://api.notion.com/v1/pages";
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=${GEMINI_API_KEY}`;

async function run() {
  // 1. ショートカットからの入力を受け取る
  let rawText = args.shortcutParameter;

  // テスト用: Scriptableアプリから直接実行した場合は入力アラートを出す
  if (!rawText) {
    let alert = new Alert();
    alert.title = "AIジャーナル入力";
    alert.message = "今の状況を入力してください\n(※通常はショートカットから音声入力で渡されます)";
    alert.addTextField("バーッと書き出す...", "");
    alert.addAction("AIで解析して送信");
    alert.addCancelAction("キャンセル");
    
    let responseIndex = await alert.presentAlert();
    if (responseIndex === -1) return;
    rawText = alert.textFieldValue(0);
  }

  if (!rawText || rawText.trim() === "") {
    console.log("テキストが空のため終了します。");
    return;
  }

  try {
    // 2. Gemini APIでテキストを解析・分類
    let parsedData = await analyzeWithGemini(rawText);
    
    // 3. Notionへ送信
    await sendToNotion(parsedData);
    
    // 成功通知
    let n = new Notification();
    n.title = "ジャーナル記録成功 ✨";
    n.body = `完了: ${parsedData.done}\n次: ${parsedData.next}`;
    n.schedule();

  } catch (error) {
    console.error(error);
    let errAlert = new Alert();
    errAlert.title = "エラーが発生しました";
    errAlert.message = error.toString();
    await errAlert.presentAlert();
  }
}

// --- Gemini API 呼び出し関数 ---
async function analyzeWithGemini(text) {
  let prompt = `
  以下のテキストは、作業中のユーザーが書いたジャーナルメモです。
  文脈を読み取り、以下の4つの要素に分類・抽出してJSON形式で出力してください。
  該当する内容がない要素は空文字("")にしてください。
  
  ユーザーの入力した文章を勝手に書き換えないでください。
  入力された生の言葉を、そのままの長さで各項目に振り分けてください。
  「えー」「あー」「んーと」などのフィラー（意味のない繋ぎ言葉）は、内容を損なわない範囲で削除してください。
  誤字脱字の修正は行ってください。
  文章の区切りがわかりにくい場合は、改行や、【。】【、】句読点などをくわえてください。

  

  【分類する項目】
  - "done": 完了したこと（簡潔なタイトルとして抽出）
  - "next": 次にやりたいこと
  - "mood": 感情・状況
  - "memo": 後でやりたいこと、今でなくてよいこと、その他のメモなど

  【入力テキスト】
  ${text}
  `;

  let req = new Request(GEMINI_API_URL);
  req.method = "POST";
  req.headers = { "Content-Type": "application/json" };
  req.body = JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: 0.4,
      responseMimeType: "application/json"
    }
  });

  let res = await req.loadJSON();
  
  if (req.response.statusCode !== 200) {
    throw new Error(`Gemini APIエラー: ${JSON.stringify(res)}`);
  }

  // Geminiからの返答(JSON文字列)を取り出してパースする
  let aiResponseText = res.candidates[0].content.parts[0].text;
  return JSON.parse(aiResponseText);
}

// --- Notion API 呼び出し関数 ---
async function sendToNotion(data) {
  // 前回同様、スラッシュを改行に変換する処理を念のため残しています
  let formatText = (text) => (text || "").replace(/スラッシュ|\/|／/g, '\n');

  let doneText = formatText(data.done);
  let nextText = formatText(data.next);
  let moodText = formatText(data.mood);
  let memoText = formatText(data.memo);

  let currentTime = new Date().toISOString();

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

  let res = await req.loadJSON();
  if (req.response.statusCode !== 200) {
    throw new Error(`Notionエラー: ${req.response.statusCode}\n${JSON.stringify(res)}`);
  }
}

// 実行
await run();
Script.complete();