# Blog 1: How Lisa Wins at Every Distance and Still Loses

Author: Jiaqi Yuan. Course: Computational Methods for Economists.

This post explains Simpson's paradox with a fictional Springfield ring-toss example. All counts are constructed teaching data. No empirical dataset is claimed.

## Files

- `Untitled.qmd`: article source; this filename preserves the website's existing post URL.
- `data/ring_toss.csv`: four fictional count rows used in the example.
- `code/reproduce.py`: standard-library Python analysis.
- `results/`: generated table, rates, and optional static chart.
- `assets/simpsons-paradox-comic.png`: supplied AI-generated comic.
- `artwork-prompt.txt`: exact final image-generation prompt and tool record.
- `interactive.html`: browser calculation and accessible interaction.
- `blog1.css`: styles scoped to this article.

## Reproduce the analysis

With Python 3.9 or later installed, run from this post's directory:

```sh
python code/reproduce.py
```

No third-party Python package is required. The script validates the four input rows, recomputes the rates and 50:50 standardization, and writes its outputs, including a scalable SVG chart. It can also run from a different working directory because its paths are relative to the script. The optional `--png` flag exports a PNG chart and requires Pillow; the supplied PNG is already generated.

The interactive panel evaluates `near_share * near_rate + (1 - near_share) * far_rate`. It starts with the original 10% / 90% near-shot shares, and the shared-mix button sets both to 50%. It reweights observed rates; it neither modifies the CSV nor simulates new throws. The article includes an explanatory fallback if JavaScript is disabled.

## Build in the existing website

Place this folder's contents in `blog/posts/post1/` of the existing Quarto website. From the website root:

```sh
quarto render blog/posts/post1/Untitled.qmd
quarto render blog/index.qmd
```

The website's existing configuration writes the rendered site to `docs/`. The blog listing uses `contents: "posts/**/*.qmd"` to discover article sources while keeping supplementary Markdown result files out of the list. Global page sources and styles do not require changes.

## Sources and artwork

- Simpson (1951), https://doi.org/10.1111/j.2517-6161.1951.tb00088.x
- Pearl (2014), *Comment: Understanding Simpson's Paradox*, UCLA author manuscript: https://ftp.cs.ucla.edu/pub/stat_ser/r414.pdf

The exact artwork is supplied, so analysis reproduction does not depend on an image-generation service. Regenerating it from the recorded prompt can produce a different illustration.

## Course alignment and submission

The main prose is designed for the assignment's approximately 400–800-word range, excluding code, tables, and figures. It introduces the puzzle, explains why it is unintuitive, derives the weighted averages, interprets both comparisons, and ends with a takeaway. Reproduction notes and references are supplementary.

The assignment asks for the published post URL. Its general instructions also request a repository URL for coding projects, while the rubric's formal checklist begins with Blog 2. Since this post supplies code, including the repository URL as well is the conservative submission choice. Publishing and assignment submission are separate from preparing these files.
