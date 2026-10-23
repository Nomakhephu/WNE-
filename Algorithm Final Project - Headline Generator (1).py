from collections import Counter
import re

STOPWORDS = {"the","is","a","an","and","or","to","of","in","on","for","with","by","at","from",
             "that","this","will","as","are","was","were","be","has","have","it","its","said",
             "new","also","but","not","they","he","she","we","into","after","before","about","over","more"}
CLICKBAIT  = ["you won't believe","shocking","unbelievable","click here","what happened next","will shock you"]
ACTION_VERBS = {"increase","decrease","reduce","announce","launch","discover","reveal","plan","warn",
                "propose","find","show","report","cut","raise","lower","approve","reject","sign",
                "pass","ban","confirm","publish","release"}
WEAK_ENDINGS = {"a","an","the","and","but","or","in","on","at","to","of","for","with","by","from",
                "that","as","near","over","after","before","its","their"}
NUMBER_PAT = re.compile(r'\b(\d[\d,]*(?:\.\d+)?\s*(?:percent|%|million|billion|trillion|thousand)?)\b', re.I)
MINOR      = {"a","an","the","and","but","or","in","on","at","to","of","for","with","by","from"}

def tokens(t):    return re.findall(r"[a-zA-Z0-9]+", t.lower())
def split_s(t):   return [s.strip() for s in re.split(r"(?<![0-9])[.!?](?=\s|$)", t) if s.strip()]
def title_c(t):   return " ".join(w.capitalize() if i==0 or w.lower() not in MINOR else w.lower() for i,w in enumerate(t.split()))
def keywords(t,n=5): return [w for w,_ in Counter(w for w in tokens(t) if w not in STOPWORDS and len(w)>2).most_common(n)]

def trim(s, n=11):
    w = s.split()
    if len(w) <= n: return s
    for i in range(n, max(n-5,3), -1):
        if w[i-1].rstrip().endswith((".","!","?")): return " ".join(w[:i]).rstrip(".!?")
        if w[i-1].rstrip().endswith((",",";")): return " ".join(w[:i]).rstrip(",;")
    cut = n
    while cut > max(n-6,3) and w[cut-1].lower().rstrip(",:;") in WEAK_ENDINGS: cut -= 1
    return " ".join(w[:cut]).rstrip(",:;")

def clean(t):
    t = re.sub(r',?\s*(?:a \w+ \w+ )?\w+ (?:called|said|dubbed|titled|named)\s+[""][^""]*[""]?','',t,flags=re.I)
    t = re.sub(r'[""][^""]*[""]?','',t)
    return re.sub(r'\s{2,}',' ',t).strip().rstrip(',:;-–—').lstrip(',:;-–—').strip()

def summarize(article):
    c = re.sub(r'[""][^""]{0,200}[""]','',article)
    c = re.sub(r',?\s+(?:a\s+\w+\s+)?(?:\w+\s+){0,4}\b(?:called|said|dubbed|titled|named|described)\b[^.!?]*','',c,flags=re.I)
    sents = split_s(re.sub(r'\s{2,}',' ',c).strip())
    if not sents: return ""
    freq, kws = Counter(tokens(article)), set(keywords(article,8))
    def score(i,s):
        toks = tokens(s)
        return -999 if len(toks)<4 else sum(freq[w] for w in set(toks)) + sum(1 for w in toks if w in kws)*2
    return re.sub(r'\.{2,}','.',max(enumerate(sents),key=lambda x:score(*x))[1]).strip().rstrip(',:;')

def candidates(article):
    sents, kws, summ = split_s(article), keywords(article,8), summarize(article)
    action = next((s for s in sents if any(v in tokens(s) for v in ACTION_VERBS)), summ)
    m = re.match(r"^([\w\s]{1,30}?)\s+(said|announced|revealed|confirmed|warned)\s+(that\s+)?(.+)",action,re.I)
    stripped = m.group(4).strip() if m and len(m.group(4).split())>=4 else action
    pool = [
        clean(title_c(trim(summ))),
        (clean(title_c(f"{kws[0].capitalize()}: {trim(summ,9)}")) if kws and not summ.lower().startswith(kws[0].lower()) else None),
        #clean(title_c(trim(action,9))) + "?",
        clean(title_c(trim(next((s for s in sents if NUMBER_PAT.search(s)),summ)))),
        clean(title_c(trim(stripped.capitalize()))),
    ]
    seen, out = set(), []
    for c in filter(None, pool):
        if c.lower().strip("?") not in seen: seen.add(c.lower().strip("?")); out.append(c)
    return out[:5]

def best_headline(cands, kws):
    vague_words = ["thing", "this", "that", "announcement", "change", "part"]

    def score(h):
        hl = h.lower()
        word_count = len(tokens(h))

        score = 0

        # Reward keyword matches
        score += sum(3 for k in kws if k in hl)

        # Penalize clickbait
        score -= sum(8 for p in CLICKBAIT if p in hl)

        # Penalize question headlines
        if "?" in h:
            score -= 6

        # Penalize vague words
        score -= sum(2 for w in vague_words if w in hl)

        # Prefer normal headline length
        if 6 <= word_count <= 14:
            score += 2
        else:
            score -= 2

        return score

    scored = [(h, score(h)) for h in cands]
    return max(scored, key=lambda x: x[1]), scored

W = 66

def display(article, n):
    cands = candidates(article); kws = keywords(article); summ = summarize(article)
    (winner,_), scored = best_headline(cands,kws)

    def wrap(text, pad=4, prefix=""):
        avail,words,lines,cur = W-pad-len(prefix)-4,text.split(),[],""
        for w in words:
            if len(cur)+len(w)+1<=avail: cur+=("" if not cur else " ")+w
            else: lines.append(cur); cur=w
        lines.append(cur); sp=" "*pad
        print(f"  │ {sp}{prefix}{lines[0]}")
        for l in lines[1:]: print(f"  │ {sp}{' '*len(prefix)}{l}")

    def sec(t): print(f"\n  ┌─ {t} {'─'*(W-len(t)-7)}┐")

    print(f"\n╔{'═'*(W-2)}╗\n║  ARTICLE {n:<{W-12}}{'':4}║\n╚{'═'*(W-2)}╝")
    sec("Summary");  wrap(summ);           print(f"  └{'─'*(W-3)}┘")
    sec("Keywords"); wrap(", ".join(kws)); print(f"  └{'─'*(W-3)}┘")
    sec("Candidates & Scores")
    for h,s in scored:
        wrap(h, prefix=f"{s:+d} {'█'*max(0,s)}{'░'*max(0,-s)}{'  ✔ WINNER' if h==winner else ''}  ")
    print(f"  └{'─'*(W-3)}┘\n\n  ✔  {winner}\n{'─'*W}")

def main():
    print(f"\n{'═'*W}\n  TRUTHFUL HEADLINE GENERATOR\n{'═'*W}")
    print(f"  Paste article → press Enter twice.   Type quit to exit.\n{'─'*W}")
    n = 0
    while True:
        print("\n  Article:\n"); lines = []
        while True:
            try: line = input()
            except EOFError: print("\n  Goodbye!\n"); return
            if line.strip().lower()=="quit": print("\n  Goodbye!\n"); return
            if line=="" and lines: break
            lines.append(line)
        text = "\n".join(lines).strip()
        if text: n+=1; display(text,n)
        else: print("  (empty — try again)")

if __name__=="__main__": main()
