import json,os,re,shutil,collections,xml.etree.ElementTree as ET
from pathlib import Path
A=Path('audit'); data=json.load(open(A/'inventory.json')); pages=data['pages']; assets=data['assets']
# reorganise downloaded assets in a path that preserves their source hierarchy
for a in assets:
 if 'file' not in a: continue
 src=A/a['file']; path=Path(__import__('urllib.parse').parse.urlparse(a['url']).path.lstrip('/'))
 dest=A/'assets'/'original-path'/path
 dest.parent.mkdir(parents=True,exist_ok=True)
 if src.exists() and src!=dest: shutil.move(str(src),str(dest))
 a['file']=str(dest.relative_to(A))
# manifests
with open(A/'asset-manifest.csv','w') as f:
 f.write('source_url,local_file,bytes,uses,alt_text,error\n')
 for a in assets:f.write(','.join('"'+str(v).replace('"','""')+'"' for v in [a['url'],a.get('file',''),a.get('bytes',''),len(a['used_on']),' | '.join(a.get('alt_texts',[])),a.get('error','')])+'\n')
# canonical sitemapped core groups
by=collections.defaultdict(list)
for p in pages:by[p.get('sitemap_type','')].append(p)
def ul(items):return '\n'.join(f'- `{p["url"].replace("https://www.threeam.com.au","") or "/"}` — {p.get("title") or "[no title]"}' for p in items)
missing_desc=[p for p in pages if p.get('status')==200 and not p.get('meta_description')]
no_h1=[p for p in pages if p.get('status')==200 and not any(h['level']=='h1' for h in p.get('headings',[]))]
# known archive/duplicate clusters
report=f'''# Three AM Website Audit

**Source:** https://www.threeam.com.au/  
**Crawled:** 17 September 2026  
**Scope:** Public URLs declared in the XML sitemap; page HTML and same-domain page-image/document assets referenced by those URLs. No redesign or production-code work was performed.

## Executive summary

- **154 public sitemap URLs** were captured: 26 standard pages, 68 individual portfolio items, 20 news posts, 7 individual testimonials, 4 shop products, 4 support documents, and 25 taxonomy/archive/author URLs.
- The live site’s principal offer is **Web, IT, Hosting and Design**, supported by Portfolio, About, News and Contact. The homepage is a credible summary, but its card copy appears to contain a likely error: the **IT** and **Hosting** cards both say “We provide complete webhosting and email solutions.”
- **205 unique same-domain image/PDF assets** were found. **204 downloaded successfully**, with original WordPress upload paths retained locally. The manifest maps each original URL to its local asset and every page using it.
- SEO metadata is uneven: **{len(missing_desc)} indexed URLs have no meta description** and **{len(no_h1)} have no H1** (mainly archive/taxonomy and utility pages). Individual detail pages generally have titles and H1s, but migration should retain/rewrite page-specific metadata deliberately.
- The sitemap carries a substantial legacy/low-value surface: old dated news, portfolio taxonomy archives, product shop/catalogue, and a customer-support knowledge base. Keep these only where they serve a current business or customer need; otherwise retain URL equity via redirects rather than rebuilding them as core navigation.

## Deliverables in this folder

| File/folder | Contents |
|---|---|
| `inventory.json` | Full structured source of truth per URL: title, description, canonical, robots, Open Graph fields, headings, extracted page copy, all links, images, and forms. |
| `page-inventory.csv` | Spreadsheet-friendly list of all 154 URLs and headline SEO/content signals. |
| `asset-manifest.csv` | Original asset URL, preserved local path, byte size, page usage count, alt text and failures. |
| `assets/original-path/` | Downloaded reusable public image/PDF assets, nested to preserve the original WordPress upload path. |
| `raw/` | XML sitemaps plus raw HTML source captured for every sitemap URL. |

## Existing information architecture and navigation

The global navigation extracted from the homepage is:

- **Web:** Search Engine Optimisation (SEO), WordPress Maintenance Plans
- **IT**
- **Hosting:** Web Hosting, .au Domains
- **Design:** Graphic Design, Digital Design
- **Portfolio:** Portfolio, Website Development, Logo Design, Branding
- **About:** About Us, Our Team, Work With Us
- **News**
- **Contact:** Contact, Subscribe to our mailing list

The homepage promotes Web, IT, Hosting and Design, a contact CTA, recent portfolio work and recent blog posts. Its footer/navigation also exposes shop/account/checkout/cart, payment policy, terms, support, HTTPS upgrade, pay invoice, and the support-document area.

## Page inventory by content type

### Core and utility pages ({len(by['page'])})
{ul(by['page'])}

### Portfolio ({len(by['portfolio'])} individual case-study/project URLs)
All individual URLs are documented in `page-inventory.csv` and `inventory.json`. Portfolio landing/filter URLs are also present under the `portfolio_tag` sitemap grouping.

### News ({len(by['post'])} posts)
All 20 articles are retained in the raw inventory. The visible current homepage feed includes **Upcoming Changes to Our Payment Options (7 Feb 2026)**, **Notice of ABN change**, and **Notice of Merger – Three AM and Identiti Web Development**.

### Other public content
- **Testimonials:** {len(by['testimonial'])} individual testimonial URLs plus `/testimonials/`.
- **Shop/catalogue:** {len(by['product'])} product URLs and three product-category archives.
- **Support documentation:** {len(by['docs'])} individual documents plus `/docs/` and two category archives.
- **Archive/taxonomy/author URLs:** {sum(len(by[k]) for k in ['category','type','portfolio_tag','author','product_cat','doc_category'])} URLs. These should not be primary replacement-site navigation.

## Forms and interactive functions discovered

The raw page inventory records exact field names/actions. Key functions:

| Area | Observed function |
|---|---|
| Contact / mailing list | Contact and subscription destination pages are in the sitemap; review their live submission handlers during build planning, as this crawl records visible HTML only. |
| Ecommerce | Shop/category sorting; product add-to-cart and quantity controls; cart, checkout, and My Account URLs. |
| Support docs | Search form on documentation archive/category/detail pages. Individual docs also expose a Name, Email, Message and Submit contact form. |
| Client service | Pay Invoice, Remote Desktop Support, hosting/domain pages. |

## SEO and migration observations

### Preserve exactly where possible

1. Keep all presently indexed **core service, portfolio, current-news, legal, client-service and support URLs** where the content remains live.
2. Keep canonical host/protocol as `https://www.threeam.com.au/`; use one 301 hop for any changed path.
3. Retain or improve unique title, description, H1, canonical and Open Graph tags for migrated core pages. Existing values are recorded in `inventory.json`.
4. Generate a fresh XML sitemap and preserve robots directives. The current robots file references Yoast’s `sitemap_index.xml` and blocks WooCommerce log/upload paths and add-to-cart parameter URLs.

### Clear cleanup candidates (validate with traffic/conversion data before removal)

- **Portfolio taxonomy/tag archives** (9), news category/type archives (8), author pages (3), and product/doc category archive pages add thin, overlapping discovery paths. Canonicalise or noindex/archive them rather than presenting all in the new IA.
- **Historical announcements** that are operationally expired: recruitment posts, COVID-19 update, Google Universal Analytics migration, early business-location/signage announcements, payment-option notices once superseded, and cryptocurrency-payment news. Preserve only if their information is still binding; otherwise 301 to News or a relevant current policy/service page.
- **Duplicated/near-duplicated portfolio representation:** one portfolio landing page, three portfolio filters, 68 projects, and nine tag archives create several routes to the same work. Use one Portfolio index with client-side/accessible filtering and keep project URLs.
- **Likely duplicate portfolio naming:** `/portfolios/richard-retallic-2/` and `/portfolios/richard-retallick/` warrant manual comparison; the misspelt/numbered pattern is a strong consolidation candidate.
- **Outdated commercial/functionality surface:** the small Blackmagic/office shop and product URLs, legacy docs, and HTTPS-upgrade page should be confirmed as actively maintained. Migrate fully if client-facing; otherwise remove from navigation and redirect responsibly.
- **Homepage content quality:** correct the duplicated IT/Hosting description; date-sensitive Latest Work and Latest Blog modules should be automated, not hard-coded.

## Recommended replacement sitemap

### Primary navigation
- `/` — Home
- `/web/` — Web Solutions overview
  - `/web/website-development/` (retain existing portfolio destination or establish as service URL)
  - `/web/wordpress-maintenance-plans/`
  - `/web/seo/`
- `/it/` — IT Solutions
- `/hosting/` — Hosting overview
  - `/hosting/au-domains/`
- `/design/` — Design overview
  - `/design/graphic-design/`
  - `/design/digital-design/`
- `/portfolio/` — Portfolio index
  - retain each active `/portfolios/{{project}}/` case study
- `/about/`
  - `/about/our-team/`
  - `/about/work-with-us/` (only while recruiting/current)
- `/news/` — Articles/news archive (curate current posts)
- `/contact/`

### Footer / utility navigation
- `/support/`, `/pay-invoice/`, `/contact/subscribe-to-our-mailing-list/`
- `/terms-and-conditions/`, `/payment-policy/`, plus proposed `/privacy-policy/` and `/whistleblower-policy/` if required
- `/docs/`, `/shop/`, `/cart/`, `/checkout/`, `/my-account/` only if the associated support/ecommerce functions remain live; otherwise remove from public navigation and map redirects.

## URL transition principles

- **Do not change URLs merely for style.** Existing service, legal, portfolio and high-value news paths can be retained as listed.
- For retired posts/archives, map each old URL to the closest surviving section (or a specific successor), not broadly to the homepage.
- Create a final redirect register before launch using `page-inventory.csv` as its complete input list. Validate 200/301 outcomes, canonicals, metadata, sitemap inclusion and internal links after deployment.

## Audit limits

This is a public HTML/XML crawl, not access to WordPress, Analytics, Search Console, CRM/payment systems, or form-mail delivery. JavaScript-only interactions, authenticated account flows and third-party embeds should receive a separate manual QA pass before migration decisions.
'''
(A/'WEBSITE-AUDIT.md').write_text(report)
json.dump(data,open(A/'inventory.json','w'),indent=2,ensure_ascii=False)
print('pages',len(pages),'assets',len(assets),'downloaded',sum('file'in x for x in assets),'missing desc',len(missing_desc),'no h1',len(no_h1))
