# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pillow",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    import tempfile
    from pathlib import Path

    import marimo as mo

    from png2svg.core import png2svg


@app.cell
def _():
    mo.md(r"""
    # png2svg explorer

    Upload a PNG picture, choose the width of the hexagons, and get a
    scalable **hexagonal SVG wallpaper**. Each hexagon is filled with the
    average color of the pixels it covers. This notebook consumes the
    `png2svg` package — it does not reimplement the conversion.
    """)
    return


@app.cell
def _():
    file = mo.ui.file(filetypes=[".png"], kind="area", label="Drop a PNG image here")
    hex_width = mo.ui.slider(
        5,
        80,
        value=20,
        step=1,
        debounce=True,  # recompute only when the slider is released
        show_value=True,
        label="Hexagon width (px)",
    )
    mo.vstack([file, hex_width])
    return file, hex_width


@app.cell
def _(file, hex_width):
    mo.stop(not file.value, mo.md("*Upload a PNG image to start.*"))

    with tempfile.TemporaryDirectory() as _tmp:
        _source = Path(_tmp) / "input.png"
        _source.write_bytes(file.contents())
        try:
            _output = png2svg(_source, Path(_tmp) / "output.svg", hex_width.value)
        except (ValueError, OSError) as _error:
            mo.stop(True, mo.callout(mo.md(f"**Conversion failed:** {_error}"), kind="danger"))
        svg = Path(_output).read_text(encoding="utf-8")
    return (svg,)


@app.cell
def _(file, svg):
    # Let the browser scale the SVG to the page width (the viewBox keeps the ratio)
    _scalable = svg.replace("<svg ", '<svg style="max-width:100%;height:auto" ', 1)
    mo.hstack(
        [
            mo.vstack([mo.md("**Original**"), mo.image(src=file.contents())]),
            mo.vstack([mo.md("**Hexagonal SVG**"), mo.Html(_scalable)]),
        ],
        widths="equal",
    )
    return


if __name__ == "__main__":
    app.run()
