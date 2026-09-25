"""Standard-library analysis: raw trials -> summaries, SVG charts, standalone result tables."""
import csv, statistics, collections, math, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
REPORT=ROOT/'report'
ALGOS=['insertion','merge','heap']
LABEL={'insertion':'삽입','merge':'병합','heap':'힙'}
KINDS={'random':'무작위','sorted':'정렬됨','reversed':'역순','few_unique':'중복 많음','nearly_sorted':'거의 정렬됨'}
COLORS={'insertion':'#bc4b36','merge':'#2264a8','heap':'#14806f'}
def summarize(name):
    groups=collections.defaultdict(list)
    with (ROOT/'data'/f'{name}raw.csv').open() as f:
        for r in csv.DictReader(f):groups[(r['kind'],int(r['n']),r['algo'])].append(r)
    out={}
    for key,rows in groups.items():
        times=[float(r['ms']) for r in rows]; qs=statistics.quantiles(times,n=4,method='inclusive')
        r=dict(kind=key[0],n=key[1],algo=key[2],median_ms=statistics.median(times),q1_ms=qs[0],q3_ms=qs[2],samples=len(rows))
        for field in ['compares','moves','buffer_bytes']:
            r[field]=int(statistics.median(int(x[field]) for x in rows))
        out[key]=r
    with (ROOT/'data'/f'{name}summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(next(iter(out.values()))));w.writeheader();w.writerows(out.values())
    return out

def chart(data,path,title):
    W,H=900,340;L,R,T,B=78,32,55,60
    vals=[r for (kind,n,a),r in data.items() if kind=='random']
    xs=sorted({r['n'] for r in vals});lo=min(r['median_ms'] for r in vals);hi=max(r['median_ms'] for r in vals)
    y0=math.floor(math.log10(lo));y1=math.ceil(math.log10(hi))
    def px(n):return L+math.log2(n/xs[0])/math.log2(xs[-1]/xs[0])*(W-L-R)
    def py(v):return H-B-(math.log10(v)-y0)/(y1-y0)*(H-T-B)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, sans-serif">',f'<rect width="{W}" height="{H}" fill="white"/>',f'<text x="{L}" y="25" font-size="18" fill="#152f44">{title}</text>']
    for exp in range(y0,y1+1):
        y=py(10**exp);parts+=[f'<line x1="{L}" y1="{y}" x2="{W-R}" y2="{y}" stroke="#e0e6eb"/>',f'<text x="{L-10}" y="{y+4}" text-anchor="end" font-size="12">{10**exp:g}</text>']
    for x in xs:
        parts.append(f'<text x="{px(x)}" y="{H-B+21}" text-anchor="middle" font-size="11">{x:,}</text>')
    for a in ALGOS:
        rs=sorted([r for r in vals if r['algo']==a],key=lambda r:r['n']);points=' '.join(f'{px(r["n"])},{py(r["median_ms"])}' for r in rs)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{COLORS[a]}" stroke-width="2.6"/>')
        for r in rs:
            x=px(r['n']);y=py(r['median_ms']);yq1=py(r['q1_ms']);yq3=py(r['q3_ms'])
            parts += [f'<line x1="{x}" y1="{yq1}" x2="{x}" y2="{yq3}" stroke="{COLORS[a]}" stroke-width="2"/>',f'<circle cx="{x}" cy="{y}" r="3.5" fill="{COLORS[a]}"/>']
        parts.append(f'<text x="{L+ALGOS.index(a)*155}" y="{H-7}" font-size="13" fill="{COLORS[a]}">{a}</text>')
    parts += [f'<text x="8" y="{T-12}" font-size="12">CPU ms</text>',f'<text x="{W-R}" y="{H-7}" text-anchor="end" font-size="12">n (log2); time (log10); median; Q1-Q3</text>','</svg>']
    path.write_text('\n'.join(parts))

def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n'

def main():
    s=summarize('');g=summarize('large-');chart(s,REPORT/'growth.svg','Input size and runtime');chart(g,REPORT/'large-growth.svg','Large-input runtime growth')
    def r(k,a,n=8192):return s[k,n,a]
    timing=table(['입력 (n=8,192)','삽입 ms','병합 ms','힙 ms'],[[KINDS[k]]+[f'{r(k,a)["median_ms"]:.4f}' for a in ALGOS] for k in KINDS])
    counts=table(['정렬 / 무작위 n=8,192','비교 횟수','이동 횟수','원소 저장 공간'],[[LABEL[a],f'{r("random",a)["compares"]:,}',f'{r("random",a)["moves"]:,}',f'{r("random",a)["buffer_bytes"]:,} B'] for a in ALGOS])
    large_rows=[]
    for n in sorted({key[1] for key in g}):
        row=[f'{n:,}']
        for a in ALGOS:
            x=g.get(('random',n,a));prev=g.get(('random',n//2,a))
            row.append('미측정' if x is None else f'{x["median_ms"]:.3f}'+(f' (×{x["median_ms"]/prev["median_ms"]:.2f})' if prev else ''))
        large_rows.append(row)
    bigtable=table(['n','삽입 ms (직전 대비)','병합 ms (직전 대비)','힙 ms (직전 대비)'],large_rows)
    results = '# 실측 결과 표 (자동 생성)\n\nREPORT.md는 검수한 원본이며 이 프로그램은 덮어쓰지 않는다.\n\n'
    results += '## 입력 형태별 시간\n\n' + timing + '\n## 연산량과 메모리\n\n' + counts + '\n## 큰 입력 실험\n\n' + bigtable
    (REPORT/'RESULTS.md').write_text(results)
    print('Generated summaries, two SVG charts and RESULTS.md; preserved REPORT.md and AI_LEARNING.md')
if __name__=='__main__':main()
