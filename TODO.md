<!--
SPDX-FileCopyrightText: 2021 Robin Vobruba <hoijui.quaero@gmail.com>

SPDX-License-Identifier: CC0-1.0
-->

## TODO (MoVeDo Filters)

- [x] header-structure-extractor (also collects statistics about headers, like: number of headers in total, number of headers per level, min level, max level)
- [ ] replace-missing-images-with-generated-SVGs ("missing image!" + ugly graphics + denoting the original path + original caption; takes parameters: flat_storage(bool), storag_root(path-to-dir))
- [ ] write test with many different headers (number and special chars too), and checkout generated references in different markdown flavours
- [x] in [linearize_links.py](linearize_links.py) (or maybe in the linearize script or in an other filter? better in [linearize_links.py](linearize_links.py)!): we also need to add an HTML anchor/reference at the start of the file, with the name of the file, cleaned (eg: `dir/file.md` -> `dir-file`)
- [x] on links targets like `#example`, we have to prepend the file-name, like: `39_pp#example`, before adding local dir prefixes and so on
