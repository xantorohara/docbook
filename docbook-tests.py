import unittest
import docbook


class Tests(unittest.TestCase):
    def test_translate_filename1(self):
        out_file = docbook.Docbook('article-abc.md', 'article-abc.html')\
            .translate_file_path('article-abc.md')
        self.assertEqual(out_file, 'article-abc.html')

    def test_translate_filename2(self):
        out_file = docbook.Docbook('in/article-abc.md', 'out/article-abc.html')\
            .translate_file_path('in/article-abc.md')
        self.assertEqual(out_file, 'out/article-abc.html')

    def test_translate_filename3(self):
        out_file = docbook.Docbook('in/*.md', 'out/{1}.html')\
            .translate_file_path('in/article-abc.md')
        self.assertEqual(out_file, 'out/article-abc.html')

    def test_translate_filename4(self):
        out_file = docbook.Docbook('in/*/doc.md', 'out/{1}.html')\
            .translate_file_path('in/article-abc/doc.md')
        self.assertEqual(out_file, 'out/article-abc.html')

    def test_translate_filename5(self):
        out_file = docbook.Docbook('in/*/doc.md', 'out/{1}/index.html')\
            .translate_file_path('in/article-abc/doc.md')
        self.assertEqual(out_file, 'out/article-abc/index.html')

    def test_translate_filename6(self):
        out_file = docbook.Docbook('in/*/*.md', 'out/{2}-{1}.html')\
            .translate_file_path('in/article/abc.md')
        self.assertEqual(out_file, 'out/abc-article.html')

    def test_translate_filename7(self):
        out_file = docbook.Docbook('in/*/*.md', 'out/{2}-{2}.html')\
            .translate_file_path('in/article/abc.md')
        self.assertEqual(out_file, 'out/abc-abc.html')

    def test_load_file_as_string(self):
        file_content = docbook.Docbook('', '').load_file_as_string('LICENSE')
        self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"', file_content)


if __name__ == '__main__':
    unittest.main()
