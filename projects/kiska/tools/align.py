import re, json, sys
from pocketsphinx import Decoder
script = open(sys.argv[1]).read()
body = script.split("## Script")[1].split("## Voice")[0].split("\n", 1)[1]
words = re.findall(r"[A-Za-z']+", body.replace("1943", "nineteen forty three").replace("-", " "))
d = Decoder(samprate=16000, bestpath=False)
for w in set(x.lower() for x in words):
    if d.lookup_word(w) is None: print("OOV", w)
d.add_word("unluckily", "AH N L AH K AH L IY", True)
d.set_align_text(" ".join(w.lower() for w in words))
raw = open("voice/voice16.raw", "rb").read()
d.start_utt(); d.process_raw(raw, full_utt=True); d.end_utt()
segs = [(s.word, s.start_frame / 100, s.end_frame / 100) for s in d.seg()]
out = [(w, s, e) for w, s, e in segs if w not in ("<s>", "</s>", "<sil>", "(NULL)")]
print(len(out), "aligned of", len(words))
json.dump([{"w": orig, "s": round(s, 3), "e": round(e + 0.01, 3)} for orig, (w, s, e) in zip(words, out)], open("voice/words.json", "w"), indent=0)
for orig, (w, s, e) in list(zip(words, out))[:12] + list(zip(words, out))[-6:]: print(orig, w, s, e)
