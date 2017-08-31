# DocBook
Generate html book or static site from Markdown files

## Use-cases:
- Generate a single html from a .md file
- Scan files using glob pattern and generate multiple output files


## Command line parameters
- --src - Source docs. Can be glob pattern with \* and ? characters
- --out - Output docs. Can have placeholders to substitute values based on source pattern
- --exclude - Subset of source files to exclude from processing
- --tpl - Template file. Default: "docbook-template.html"
- --props - Default properties file. Default "docbook.properties"

## Usage samples
```bash 
python -m docbook --src=docbook.md --out=docbook.html
python -m docbook --src=source/page-*.md --out=output/{1}.html
```

## File names transformation
### Single files transformation samples

- from "article-abc.md" to "article-abc.html"
```--src=article-abc.md --out=article-abc.html```

- from "articles/article-abc.md" to "public/article-abc.html"
```--src=articles/article-abc.md --out=public/article-abc.html```


## File patterns

- from "articles/\*.md" to  "public/\*.html"
```--src=articles/*.md --out=public/{1}.html```

- from "articles/\*/doc.md" to "public/\*.html"
```--src=articles/*/doc.md --out=public/{1}.html```

- from "articles/\*/doc.md" to "public/\*/index.html"
```--src=articles/*/doc.md --out=public/{1}/index.html```

- from "articles/\*/\*.md" to "public/\*-\*.html"
```--src=articles/*/*.md --out=public/{1}-{2}.html```
 
## Sites using DocBook
- [Orange-Pi tips and tricks](https://orange-pi.github.io/)
- [Spring Field](https://xantorohara.github.io/spring-field/)
- [Spotfire Internals](https://xantorohara.github.io/spotfire-internals/)
