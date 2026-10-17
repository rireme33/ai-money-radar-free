import unittest
from scripts.collect import parse_feed, select, canonical

RSS = b'<rss><channel><item><title>Show HN: AI workflow SaaS</title><link>https://example.com/a?utm_source=x</link><description>AI product</description></item><item><title>Cat pictures</title><link>https://example.com/cats</link></item></channel></rss>'

class TestCollector(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(len(list(parse_feed(RSS))), 2)
    def test_select(self):
        rows = list(parse_feed(RSS))
        data = select(rows, [])
        self.assertEqual(len(data),1)
        self.assertFalse(data[0]['revenue_verified'])
        self.assertEqual(len(select(rows,data)),1)
    def test_canonical(self):
        self.assertEqual(canonical('HTTPS://Example.COM/a/?x=y'), 'https://example.com/a')
if __name__=='__main__': unittest.main()
