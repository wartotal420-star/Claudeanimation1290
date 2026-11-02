# Split the aligned narration into chapters 2-14: chNN.wav (2.0 s lead-in for the chapter card, the chapter's
# sentences, 0.8 s tail) + chNN_words.json [{w, s, e, line}] in chapter-local seconds + chNN_lines.json.
#   python3 tools/chapters.py <SCRIPT.md> <voiceDir>      (voiceDir has v1/v2/v3.wav + words_vN(_lines).json)
import re, json, sys, os, subprocess
import numpy as np

SCRIPT, VD = sys.argv[1:3]
LEAD, TAIL, SR = 2.0, 0.8, 48000
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", re.sub(r"\[[^]]*\]", " ", s.lower())).strip()

# chapter texts from the script
chap, cur = {}, None
for line in open(SCRIPT).read().splitlines():
    m = re.match(r"## (\d+)\. ", line)
    if m: cur = int(m.group(1)); chap[cur] = ""; continue
    if line.startswith("## "): cur = None
    elif cur is not None: chap[cur] += " " + line
chapN = {k: norm(v) for k, v in chap.items()}

def load(v):
    return json.load(open(f"{VD}/words_v{v}.json")), json.load(open(f"{VD}/words_v{v}_lines.json"))
pcm = {}
def audio(v):
    if v not in pcm:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{VD}/v{v}.wav", "-ar", str(SR), "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout
        pcm[v] = np.frombuffer(raw, np.int16)
    return pcm[v]

# every sentence of v1 / v2 / v3 in order, labelled with its chapter (the next chapter wins ties at boundaries)
seq, last = [], 0
for v in (1, 2, 3):
    W, L = load(v)
    for l in L:
        if v == 2 and l["k"] == 0 and norm(l["text"]) == "they choose force": continue   # repeated across files
        t = norm(l["text"]); hits = [c for c in sorted(chapN) if t and t in chapN[c] and c >= last]
        c = hits[0] if hits else last
        last = c
        seq.append({"v": v, "k": l["k"], "s": l["s"], "e": l["e"], "text": l["text"], "ch": c, "words": [w for w in W if w["line"] == l["k"]]})
unmatched = [x["text"] for x in seq if norm(x["text"]) not in chapN.get(x["ch"], "")]
print("sentences", len(seq), "unmatched", len(unmatched), unmatched[:5])
summary = {}
for c in sorted({x["ch"] for x in seq}):
    if c < 2: continue
    S = [x for x in seq if x["ch"] == c]
    parts, words, lines, t = [np.zeros(int(LEAD * SR), np.int16)], [], [], LEAD
    # keep the natural pauses: take each run of consecutive sentences from one file as one continuous slice
    i = 0
    while i < len(S):
        j = i
        while j + 1 < len(S) and S[j + 1]["v"] == S[i]["v"] and S[j + 1]["k"] == S[j]["k"] + 1: j += 1
        v, a, b = S[i]["v"], max(0.0, S[i]["s"] - 0.08), S[j]["e"] + 0.25
        x = audio(v)[int(a * SR): int(b * SR)]
        for s in S[i: j + 1]:
            lines.append({"k": len(lines), "text": s["text"], "s": round(s["s"] - a + t, 3), "e": round(s["e"] - a + t, 3)})
            for w in s["words"]: words.append({"w": w["w"], "s": round(w["s"] - a + t, 3), "e": round(w["e"] - a + t, 3), "line": lines[-1]["k"]})
        parts.append(x); t += len(x) / SR
        if j + 1 < len(S): parts.append(np.zeros(int(0.35 * SR), np.int16)); t += 0.35
        i = j + 1
    parts.append(np.zeros(int(TAIL * SR), np.int16)); t += TAIL
    y = np.concatenate(parts)
    name = f"ch{c:02d}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", f"{VD}/{name}.wav"], input=y.tobytes())
    json.dump(words, open(f"{VD}/{name}_words.json", "w")); json.dump(lines, open(f"{VD}/{name}_lines.json", "w"), indent=0)
    summary[name] = {"seconds": round(t, 2), "frames": int(round(t * 30)), "sentences": len(S), "words": len(words)}
    print(name, summary[name])
json.dump(summary, open(f"{VD}/chapters.json", "w"), indent=1)
