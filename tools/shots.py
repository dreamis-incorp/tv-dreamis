import sys, asyncio, subprocess, time, os
from playwright.sync_api import sync_playwright
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
srv = subprocess.Popen(['python3','-m','http.server','8765','-d','site'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = b.new_page(viewport={'width':1080,'height':1920})
        logs=[]; pg.on('console', lambda m: logs.append(m.text)); pg.on('pageerror', lambda e: logs.append('ERR '+str(e)))
        pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(800)
        pg.screenshot(path=f'{out}/00_gate.png')
        pg.fill('#gp', os.environ.get('TV_PASSWORD','teste-1234')); pg.click('#gf button')
        pg.wait_for_timeout(2500)
        n = pg.evaluate('order.length')
        print('slides', n)
        for i in range(n):
            pg.evaluate(f'paused=true; show({i})'); pg.wait_for_timeout(900)
            pg.screenshot(path=f'{out}/{i+1:02d}.png')
        print('\n'.join(logs[:10]))
        b.close()
finally:
    srv.terminate()
