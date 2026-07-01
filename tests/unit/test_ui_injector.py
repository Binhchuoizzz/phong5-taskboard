import unittest
import re

def inject_stylesheet_html(html_content, stylesheet_href="/custom-ui.css"):
    # If the stylesheet is already present, do nothing (idempotent)
    if stylesheet_href in html_content:
        return html_content
    
    # Replace </head> with the new link tag and </head>
    link_tag = f'<link rel="stylesheet" href="{stylesheet_href}"></head>'
    
    # Case-insensitive replacement of </head>
    new_html, count = re.subn(r'(?i)</head>', link_tag, html_content, count=1)
    if count == 0:
        # Fallback if no head tag is found, append to end
        return html_content + f'\n<link rel="stylesheet" href="{stylesheet_href}">'
    return new_html

class TestUiInjector(unittest.TestCase):
    def test_injection_success(self):
        html = "<html><head><title>Test</title></head><body>Hello</body></html>"
        result = inject_stylesheet_html(html)
        self.assertIn('<link rel="stylesheet" href="/custom-ui.css"></head>', result)
        self.assertTrue(result.endswith("</html>"))

    def test_idempotency(self):
        # Already has custom-ui.css
        html = '<html><head><link rel="stylesheet" href="/custom-ui.css"></head><body>Hello</body></html>'
        result = inject_stylesheet_html(html)
        # Count occurrences of custom-ui.css
        self.assertEqual(result.count("/custom-ui.css"), 1)
        self.assertEqual(result, html)

    def test_case_insensitive_head(self):
        html = "<html><HEAD><title>Test</title></HEAD><body>Hello</body></html>"
        result = inject_stylesheet_html(html)
        self.assertIn('<link rel="stylesheet" href="/custom-ui.css"></head>', result)

    def test_fallback_no_head_tag(self):
        html = "<html><body>Hello</body></html>"
        result = inject_stylesheet_html(html)
        self.assertTrue(result.endswith('\n<link rel="stylesheet" href="/custom-ui.css">'))

if __name__ == "__main__":
    unittest.main()
