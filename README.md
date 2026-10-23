# Jiaqi Yuan's website

A personal website and a collection of economics and data-analysis articles for Computational Methods for Economists. The site is written in Quarto and published through GitHub Pages.

- **Website:** [lizzyuan77.github.io/lizzyuan-s-website](https://lizzyuan77.github.io/lizzyuan-s-website/)
- **Blog:** [All posts](https://lizzyuan77.github.io/lizzyuan-s-website/blog/)
- **Blog 6:** [Match Parents and Children with SQL in Python](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post6/)
- **Blog 5:** [Why a Tech-Rich State Can Still Have a Wide Gender Pay Gap](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post5/)
- **Reproduce Blog 6:** [Start with its README](blog/posts/post6/README.md). It needs your own free PSID extract (PSID data cannot be redistributed); the README lists every variable.
- **Reproduce Blog 5:** [Start with its README](blog/posts/post5/README.md). All data needed for that analysis are included; no Census API key or files from another computer are required.

## Repository guide

| Location | Contents |
| --- | --- |
| `_quarto.yml` | Website navigation, theme and publication settings |
| `index.qmd`, `bio.qmd`, `resume.qmd` | Editable website pages |
| `blog/index.qmd` | Blog landing page and post listing |
| `blog/posts/post1/` through `post6/` | Article source and each post's replication materials |
| `docs/` | Rendered website served by GitHub Pages |
| `images/`, `files/`, `styles.css` | Shared website assets |

Each coding post has its own README because its data, dependencies and reproduction steps differ. For Blog 5, see the [folder guide and exact commands](blog/posts/post5/README.md) and [detailed methodology](blog/posts/post5/METHODOLOGY.md).

## Edit and build the website

1. Clone this repository and open its folder.
2. Install [Quarto](https://quarto.org/docs/get-started/) and R. Follow the relevant post's README to install its analysis dependencies and regenerate results before rendering.
3. To build the website, run the following from the repository root:

   ```sh
   quarto render
   ```

4. To view a local preview:

   ```sh
   quarto preview
   ```

Quarto writes published pages to `docs/`, as configured in `_quarto.yml`. Edit the `.qmd` source files rather than the generated HTML. To publish a change, commit the source, required analysis files, and updated `docs/` output to `main`; GitHub Pages then builds and deploys the site.

## Submission links for Blog 5

Submit both links required by the assignment:

- [Published article](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post5/)
- [Repository](https://github.com/lizzyuan77/lizzyuan-s-website) — the relevant code and data are in [`blog/posts/post5/`](blog/posts/post5/).
