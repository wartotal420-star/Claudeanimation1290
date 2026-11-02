# Forced alignment for long narration files (pocketsphinx alone fails on 10+ minute files).
#   python3 tools/align_long.py <text.txt> <voice.wav> <words.json>
# 1) find the pauses in the recording, 2) map every sentence boundary to a pause with dynamic programming
#    (sentence durations ~ syllable counts), 3) align each sentence's words inside its own slice with pocketsphinx,
#    falling back to syllable-proportional timing when a slice will not align. Output: [{w, s, e, line}]
import re, json, sys, subprocess
import numpy as np
from pocketsphinx import Decoder

txt, wav, out = sys.argv[1:4]
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def two(n): return ONES[n] if n < 20 else TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
def year(m): y = int(m.group(0)); return "twenty ten" if y == 2010 else two(y // 100) + " " + two(y % 100)
def spell(n):
    if n < 100: return two(n)
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + two(n % 100))
    if n < 1000000: return spell(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + spell(n % 1000))
    return spell(n // 1000000) + " million" + ("" if n % 1000000 == 0 else " " + spell(n % 1000000))
def num(m): return spell(int(m.group(0).replace(",", "")))
def words_of(line):
    t = re.sub(r"\[[^]]*\]", " ", line)
    t = re.sub(r"\b(19|20)\d\d\b", year, t)
    t = re.sub(r"\b\d[\d,]*\b", num, t)
    return re.findall(r"[A-Za-z']+", t.replace("-", " "))
def syl(w):
    v = re.findall(r"[aeiouy]+", w.lower()); n = len(v) - (1 if w.lower().endswith("e") and len(v) > 1 else 0)
    return max(1, n)

# sentences = non-empty lines of the VO file, further split at sentence ends
S = []
for line in open(txt).read().splitlines():
    for part in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", line.strip()):
        ws = words_of(part)
        if ws: S.append({"text": part, "words": ws, "syl": sum(syl(w) for w in ws)})

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout
pcm = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
hop = 160                                                             # 10 ms
rms = np.sqrt(np.convolve(pcm ** 2, np.ones(400) / 400, "same")[::hop] + 1e-12)
db = 20 * np.log10(rms)
floor, peak = np.percentile(db, 10), np.percentile(db, 95)
thr = min(-38.0, floor + 0.12 * (peak - floor))
quiet = db < thr
# gaps: quiet runs >= 0.07 s (this narrator pauses briefly); each gap = (start, end) in seconds
gaps, i, N = [], 0, len(quiet)
while i < N:
    if quiet[i]:
        j = i
        while j < N and quiet[j]: j += 1
        if (j - i) >= 7: gaps.append((i / 100, j / 100))
        i = j
    else: i += 1
if not gaps or gaps[0][0] > 0.05: gaps.insert(0, (0.0, 0.0))
total = N / 100
gaps.append((total, total))
G = len(gaps)
speech = lambda a, b: max(0.05, gaps[b][0] - gaps[a][1])             # speech time between gap a and gap b (incl. skipped gaps)
skipped = np.zeros(G);
for g in range(G): skipped[g] = gaps[g][1] - gaps[g][0]
cum = np.concatenate([[0], np.cumsum(skipped)])
syl_total = sum(s["syl"] for s in S)
rate = syl_total / max(1, total - sum(skipped[1:-1]) * 0.85)
print(f"{len(S)} sentences, {G} pauses, {total:.1f} s, rate {rate:.2f} syl/s")

# DP: sentence k ends at gap j. cost = (log speech/expected)^2 + skipped long pauses inside the sentence
K = len(S); INF = 1e18
cost = np.full((K + 1, G), INF); back = np.zeros((K + 1, G), int)
cost[0, 0] = 0
for k in range(1, K + 1):
    exp_t = S[k - 1]["syl"] / rate
    for j in range(1, G):
        best, bi = INF, -1
        lo = j - 1
        while lo >= 0:
            if cost[k - 1, lo] < INF:
                t = gaps[j][0] - gaps[lo][1]
                if t > exp_t * 3 + 3: break
                inner = cum[j] - cum[lo + 1]                           # pause time inside this sentence
                c = cost[k - 1, lo] + np.log(max(t - inner, 0.05) / exp_t) ** 2 * 4 + inner * 1.5 - (gaps[j][1] - gaps[j][0]) * 0.8
                if c < best: best, bi = c, lo
            lo -= 1
        cost[k, j], back[k, j] = best, bi
j = G - 1 if cost[K, G - 1] < INF else int(np.argmin(cost[K]))
ends = []
for k in range(K, 0, -1): ends.append(j); j = back[k, j]
ends = ends[::-1]
bounds = []; prev = 0
for k in range(K): bounds.append((gaps[prev][1], gaps[ends[k]][0])); prev = ends[k]

d = Decoder(samprate=16000, bestpath=False)
EXTRA = {"ardennes": "AA R D EH N Z", "barbarossa": "B AA R B AH R OW S AH", "kyiv": "K IY V", "sudetenland": "S UW D EY T AH N L AE N D",
         "unluckily": "AH N L AH K AH L IY", "bagration": "B AA G R AH T IY OW N", "stauffenberg": "S T AW F AH N B ER G", "kamikazes": "K AA M IH K AA Z IY Z",
         "bletchley": "B L EH CH L IY", "onoda": "OW N OW D AH", "hiroo": "HH IH R OW", "sobibor": "S OW B IH B AO R", "treblinka": "T R AH B L IH NG K AH",
         "bastogne": "B AE S T OW N", "arnhem": "AA R N AH M", "yalta": "Y AO L T AH", "guadalcanal": "G W AA D AH L K AH N AE L", "leyte": "L EY T IY",
         "iwo": "IY W OW", "jima": "JH IY M AH", "okinawa": "OW K IH N AA W AH", "nagasaki": "N AA G AH S AA K IY", "doolittle": "D UW L IH T AH L",
         "paulus": "P AW L AH S", "kursk": "K UH R S K", "enigma": "IH N IH G M AH", "lubang": "L UW B AA NG", "nuremberg": "N UH R AH M B ER G", "af": "EY EH F", "codenamed": "K OW D N EY M D", "eardrums": "IH R D R AH M Z", "malaya": "M AH L EY AH", "riveter": "R IH V AH T ER", "unendurable": "AH N EH N D Y UH R AH B AH L"}
for w in sorted({w.lower() for s in S for w in s["words"]}):
    if d.lookup_word(w) is None:
        if w in EXTRA: d.add_word(w, EXTRA[w], False)
        else: print("OOV", w)
OUT, fails = [], 0
for k, s in enumerate(S):
    a, b = bounds[k]; a0, b0 = max(0, a - 0.12), min(total, b + 0.12)
    seg = raw[int(a0 * 16000) * 2: int(b0 * 16000) * 2]
    ws = s["words"]; got = None
    try:
        d.set_align_text(" ".join(w.lower() for w in ws))
        d.start_utt(); d.process_raw(seg, full_utt=True); d.end_utt()
        sg = [(x.start_frame / 100 + a0, x.end_frame / 100 + a0) for x in d.seg() if x.word not in ("<s>", "</s>", "<sil>", "(NULL)")]
        if len(sg) == len(ws): got = sg
    except Exception: pass
    if got is None:                                                     # syllable-proportional fallback
        fails += 1; t, tot = a, sum(syl(w) for w in ws); got = []
        for w in ws: dt = (b - a) * syl(w) / tot; got.append((t, t + dt)); t += dt
    for w, (st, en) in zip(ws, got): OUT.append({"w": w, "s": round(st, 3), "e": round(en + 0.01, 3), "line": k})
print(f"{len(OUT)} words, {fails} of {K} sentences used fallback timing")
json.dump(OUT, open(out, "w"))
json.dump([{"k": k, "text": s["text"], "s": bounds[k][0], "e": bounds[k][1]} for k, s in enumerate(S)], open(out.replace(".json", "_lines.json"), "w"), indent=0)
