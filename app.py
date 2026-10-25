import os, requests
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
SYSTEM = """أنت مساعد عراقي ودود اسمك مساعدي العراقي. تحدث طبيعياً باللهجة الجنوبية العراقية، خاصة الناصرية والبصرة. استخدم عيني، شلونك، شنو، هسّه، آني، تدلّل عند ملاءمتها. كن واضحاً ومحترماً ولا تدّع أنك إنسان. لا تخترع معلومات."""
@app.get("/")
def home(): return render_template("index.html")
@app.post("/api/chat")
def chat():
    key=os.getenv("GEMINI_API_KEY","").strip()
    if not key: return jsonify(error="مفتاح Gemini غير مضبوط. شغّل start_windows.bat."),503
    data=request.get_json(silent=True) or {}; msgs=data.get("messages",[])
    contents=[]
    for m in msgs[-16:]:
        if m.get("role") in ("user","model") and isinstance(m.get("content"),str) and m["content"].strip():
            contents.append({"role":m["role"],"parts":[{"text":m["content"].strip()[:6000]}]})
    if not contents or contents[-1]["role"]!="user": return jsonify(error="اكتب رسالة أولاً عيني."),400
    try:
        r=requests.post(API_URL,headers={"x-goog-api-key":key,"Content-Type":"application/json"},
          json={"systemInstruction":{"parts":[{"text":SYSTEM}]},"contents":contents,
                "generationConfig":{"temperature":0.8,"maxOutputTokens":700}},timeout=45)
        if r.status_code>=400:
            detail=r.json().get("error",{}).get("message","")
            msg="مفتاح API غير صحيح أو ما عنده صلاحية." if r.status_code in (401,403) else ("وصلت لحد الاستخدام؛ جرّب لاحقاً." if r.status_code==429 else "صار خطأ من خدمة الذكاء الاصطناعي.")
            return jsonify(error=msg,detail=detail[:400]),502
        js=r.json(); parts=js.get("candidates",[{}])[0].get("content",{}).get("parts",[])
        answer="\n".join(p.get("text","") for p in parts if p.get("text"))
        return jsonify(reply=answer) if answer else (jsonify(error="ما وصلني رد نصّي. جرّب مرة ثانية."),502)
    except requests.Timeout: return jsonify(error="الرد تأخر. تأكد من الإنترنت وجرّب مرة ثانية."),504
    except Exception: return jsonify(error="تعذّر الاتصال بالخدمة. تأكد من الإنترنت."),502
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5050")), debug=False)
