import urllib.request
import json

BASE = 'http://127.0.0.1:8000'

# 1. Test HTML
html = urllib.request.urlopen(f'{BASE}/').read().decode('utf-8')
assert 'selected-doc-dossier' in html, 'Missing selected-doc-dossier container'
assert 'docs-cards-grid' in html, 'Missing docs-cards-grid'
assert 'doc-dossier-modal' in html, 'Missing doc-dossier-modal'
print('[PASS] HTML structure contains all new PDF selection components.')

# 2. Test CSS
css = urllib.request.urlopen(f'{BASE}/static/css/styles.css').read().decode('utf-8')
assert '.docs-cards-grid' in css
assert '.doc-select-card' in css
assert '.doc-dossier-panel' in css
assert '.page-pill' in css
print('[PASS] CSS contains all required styling rules.')

# 3. Test JS
js = urllib.request.urlopen(f'{BASE}/static/js/app.js').read().decode('utf-8')
assert 'selectDocument' in js
assert 'openDocumentModal' in js
assert 'renderDossierIntoContainer' in js
print('[PASS] JavaScript contains all interactive dossier functions.')

# 4. Test API
docs = json.loads(urllib.request.urlopen(f'{BASE}/api/documents').read().decode('utf-8'))
print(f'[INFO] Found {len(docs)} documents in database.')

for d in docs:
    doc_id = d['id']
    doc_name = d['filename']
    
    # Test lookup by ID
    res1 = json.loads(urllib.request.urlopen(f'{BASE}/api/documents/{doc_id}').read().decode('utf-8'))
    # Test lookup by filename (URL encoded)
    encoded_name = urllib.parse.quote(doc_name)
    res2 = json.loads(urllib.request.urlopen(f'{BASE}/api/documents/{encoded_name}').read().decode('utf-8'))
    
    assert res1['document']['id'] == doc_id
    assert res2['document']['id'] == doc_id
    assert 'profile' in res1
    assert 'executive_summary' in res1['profile']
    assert 'key_highlights' in res1['profile']
    assert len(res1['facts']) == d['fact_count']
    assert len(res1['pages']) == d['page_count']
    print(f'  [PASS] {doc_name}: {d["page_count"]} pages, {d["fact_count"]} facts, {len(res1["relationships"])} rels, {len(res1["profile"]["key_highlights"])} highlights')

print('\n[ALL PASS] Every single PDF can be selected, individually inspected, and returns full dossiers!')
