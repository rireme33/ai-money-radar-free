import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestStaticSite(unittest.TestCase):
    def test_required_files_exist(self):
        for name in ('index.html', 'styles.css', 'app.js', 'data/leads.json'):
            self.assertTrue((ROOT / name).is_file(), name)

    def test_page_has_product_and_sales_links(self):
        page = (ROOT / 'index.html').read_text('utf-8')
        self.assertIn('AIに', page)
        self.assertIn('「次に売るもの」', page)
        self.assertIn('data/leads.json', (ROOT / 'app.js').read_text('utf-8'))
        self.assertGreaterEqual(page.count('https://note.com/rireme33/n/n64e45df6f23f'), 2)

    def test_leads_match_frontend_contract(self):
        leads = json.loads((ROOT / 'data/leads.json').read_text('utf-8'))
        self.assertIsInstance(leads, list)
        required = {'title', 'source_url', 'added_utc'}
        for lead in leads:
            self.assertTrue(required.issubset(lead))
            self.assertTrue(lead['source_url'].startswith(('http://', 'https://')))


if __name__ == '__main__':
    unittest.main()
