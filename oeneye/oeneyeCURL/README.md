# oeneyeCURL

A curl wrapper that knows OENEYE OS Project assets by name, so you don't
have to remember Zenodo record IDs or exact filenames.

## Usage

```bash
chmod +x oeneyeCURL.sh

./oeneyeCURL.sh list                 # see what it knows about
./oeneyeCURL.sh logo                 # -> ./oeneye-logo.png
./oeneyeCURL.sh logo /tmp/logo.png   # custom output path
./oeneyeCURL.sh wg-server            # -> ./oeneye-wg-server.zip
./oeneyeCURL.sh distro-logo          # -> ./oeneye-distro-logo.zip
./oeneyeCURL.sh about                # project blurb + citation
./oeneyeCURL.sh cite                 # BibTeX stub
```

## Known assets

| name          | source                                              |
|---------------|------------------------------------------------------|
| `logo`        | canonical oeneye logo PNG (Zenodo record 22973195)   |
| `wg-server`   | `oeneye-wg-server.zip` (Zenodo record 22973347)      |
| `distro-logo` | `oeneye-distro-logo.zip` (Zenodo record 22973347)    |

New assets are added by adding one line to the `ASSETS` associative array
at the top of `oeneyeCURL.sh`:

```bash
[some-name]="https://zenodo.org/records/.../files/....?download=1|default-filename"
```

## Integration

`oeneye-set-distro-logo.sh` auto-detects `oeneyeCURL.sh` if it's sitting in
the same directory and uses it to fetch the default logo; otherwise it
falls back to a plain `curl` call to the same URL. Keep the two scripts
together for that to kick in.

## Citation

```bibtex
@misc{oeneyecurl2026,
  author    = {Ketelhut, Kai Olaf},
  title     = {DIY distro logo (oeneyeCURL asset registry)},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22973347},
  url       = {https://doi.org/10.5281/zenodo.22973347},
  note      = {Curatorium / OENEYE OS Project. org-curatorium community. CC-BY-4.0}
}
```
