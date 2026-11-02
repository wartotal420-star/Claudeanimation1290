# forced alignment of a narration text file to a wav (pocketsphinx), writes words.json [{w, s, e}]
import re, json, sys, subprocess
from pocketsphinx import Decoder
txt, wav, out = sys.argv[1:4]
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def two(n): return ONES[n] if n < 20 else TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
def year(m):
    y = int(m.group(0))
    if y == 2010: return "twenty ten"
    return two(y // 100) + " " + two(y % 100)
t = open(txt).read().replace("[beat]", " ")
t = re.sub(r"\[[^]]*\]", " ", t)
t = re.sub(r"\b(19|20)\d\d\b", year, t)
words = re.findall(r"[A-Za-z']+", t.replace("-", " "))
d = Decoder(samprate=16000, bestpath=False)
EXTRA = {"ardennes": "AA R D EH N Z", "barbarossa": "B AA R B AH R OW S AH", "kyiv": "K IY V", "sudetenland": "S UW D EY T AH N L AE N D",
         "unluckily": "AH N L AH K AH L IY", "bagration": "B AA G R AH T IY OW N", "stauffenberg": "S T AW F AH N B ER G", "kamikazes": "K AA M IH K AA Z IY Z",
         "bletchley": "B L EH CH L IY", "onoda": "OW N OW D AH", "hiroo": "HH IH R OW", "sobibor": "S OW B IH B AO R", "treblinka": "T R AH B L IH NG K AH",
         "bastogne": "B AE S T OW N", "arnhem": "AA R N AH M", "yalta": "Y AO L T AH", "guadalcanal": "G W AA D AH L K AH N AE L", "leyte": "L EY T IY",
         "iwo": "IY W OW", "jima": "JH IY M AH", "okinawa": "OW K IH N AA W AH", "nagasaki": "N AA G AH S AA K IY", "doolittle": "D UW L IH T AH L",
         "paulus": "P AW L AH S", "kursk": "K UH R S K", "enigma": "IH N IH G M AH", "lubang": "L UW B AA NG", "nuremberg": "N UH R AH M B ER G", "af": "EY EH F", "codenamed": "K OW D N EY M D", "eardrums": "IH R D R AH M Z", "malaya": "M AH L EY AH", "riveter": "R IH V AH T ER", "unendurable": "AH N EH N D Y UH R AH B AH L"}
for w in sorted(set(x.lower() for x in words)):
    if d.lookup_word(w) is None:
        if w in EXTRA: d.add_word(w, EXTRA[w], False)
        else: print("OOV", w)
d.add_word("<dummy>", "AH", True)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ar", "16000", "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout
d.set_align_text(" ".join(w.lower() for w in words))
d.start_utt(); d.process_raw(raw, full_utt=True); d.end_utt()
segs = [(s.word, s.start_frame / 100, s.end_frame / 100) for s in d.seg() if s.word not in ("<s>", "</s>", "<sil>", "(NULL)")]
print(len(segs), "aligned of", len(words))
json.dump([{"w": o, "s": round(s, 3), "e": round(e + 0.01, 3)} for o, (w, s, e) in zip(words, segs)], open(out, "w"))
