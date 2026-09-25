/* PDF export from the Markdown source. npm packages: marked, playwright.
 * MERMAID_JS points to mermaid@10.9.3/dist/mermaid.min.js.
 * CHROME_PATH may specify an installed Chromium/Chrome executable. */
const fs=require('fs'), path=require('path');
const {pathToFileURL}=require('url');
const {chromium}=require('playwright');
(async()=>{
 const {marked}=await import(pathToFileURL(require.resolve('marked')).href);
 const root=path.resolve(__dirname,'..');
 const src=fs.readFileSync(path.join(root,'report/REPORT.md'),'utf8');
 const pages=src.split('<!-- PAGE -->').map(x=>'<section class="page">'+marked.parse(x)+'</section>').join('\n');
 const html=`<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
 @page {size:A4;margin:15mm 16mm 16mm;} *{box-sizing:border-box}
 body{font-family:'Apple SD Gothic Neo','Noto Sans CJK KR',sans-serif;font-size:9.7pt;line-height:1.52;color:#233342;margin:0}
 .page{break-after:page;} .page:last-of-type{break-after:auto}
 h1{font-size:24pt;letter-spacing:-.6pt;margin:0 0 12pt;color:#15374d}
 h2{font-size:17pt;margin:0 0 12pt;padding-bottom:8pt;border-bottom:2pt solid #14806f;color:#15374d}
 h1+h2{margin-top:15pt} h3{font-size:11.8pt;color:#15374d;margin:10pt 0 5pt}
 p{margin:5pt 0 7pt} table{width:100%;border-collapse:collapse;font-size:8.8pt;margin:8pt 0}
 th{background:#edf3f6;text-align:left;color:#15374d} th,td{padding:4.8pt 6pt;border-bottom:0.5pt solid #d5e0e7}
 tr{break-inside:avoid} a{color:#2264a8;overflow-wrap:anywhere;text-decoration:none}
 blockquote{margin:8pt 0;padding:7pt 10pt;border-left:3pt solid #c49732;background:#fbf6e9;font-size:9pt}
 blockquote p{margin:0}pre{padding:10pt;background:#f1f5f8;font-size:8.8pt;white-space:pre-wrap}
 code{font-family:Menlo,monospace;font-size:.87em}
 img{display:block;max-width:100%;margin:9pt auto}
 .mermaid{display:flex;justify-content:center;margin:10pt 0;max-height:155px}
 .mermaid svg{max-width:100%;max-height:155px!important;height:auto}
 .page:nth-of-type(2) .mermaid{max-height:245px}.page:nth-of-type(2) .mermaid svg{max-height:245px!important}
 ol{padding-left:17pt;font-size:9pt}li{margin-bottom:5pt}
 </style></head><body>${pages}</body></html>`;
 fs.mkdirSync(path.join(root,'tmp/pdfs'),{recursive:true});
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 const page=await browser.newPage({viewport:{width:900,height:1200}});
 await page.setContent(html);
 await page.evaluate(()=>{document.querySelectorAll('pre code.language-mermaid').forEach(c=>{let div=document.createElement('div');div.className='mermaid';div.textContent=c.textContent;c.parentNode.replaceWith(div)});});
 await page.addScriptTag({path:process.env.MERMAID_JS});
 await page.evaluate(async()=>{mermaid.initialize({startOnLoad:false,theme:'base',themeVariables:{primaryColor:'#eef5f8',primaryTextColor:'#17384c',primaryBorderColor:'#2264a8',lineColor:'#14806f',fontFamily:'Apple SD Gothic Neo, sans-serif'},flowchart:{htmlLabels:false}});await mermaid.run();});
 const imagePaths=await page.locator('img').evaluateAll(imgs=>imgs.map(i=>i.getAttribute('src')));
 for(const src of imagePaths){const buffer=fs.readFileSync(path.join(root,'report',src));await page.locator(`img[src="${src}"]`).evaluate((el,data)=>el.src='data:image/svg+xml;base64,'+data,buffer.toString('base64'));}
 await page.evaluate(()=>document.fonts.ready);
 // Self-contained rendered HTML for optional browser review.
 fs.writeFileSync(path.join(root,'tmp/pdfs/report.html'),await page.content());
 await page.pdf({path:path.join(root,'output/pdf/compare-sorting.pdf'),printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;color:#657889;width:100%;margin:0 16mm;display:flex;justify-content:space-between"><span>Compare sorting · 김형균 2022193003</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'});
 console.log('Rendered',await page.locator('.mermaid svg').count(),'Mermaid diagrams');
 await browser.close();
})();
