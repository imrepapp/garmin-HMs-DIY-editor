# HMs DIY Editor

A browser-based layout designer for the Garmin Connect IQ data field **HMs DIY**
(a freely buildable data field by hundsmiachn). The original Designer is Windows-only;
this editor runs anywhere, reads and writes the same XML layouts, and produces the
**layout string** that goes into the data field's settings.

## Use

Open `index.html` in a browser. It is a single file with no build step.

- **Add** values, labels, lines, frames, circles, arcs, filling gauge arcs, progress bars, graphs and direction markers.
- **Edit on the screen**: drag, resize with handles, snap to other elements and the centre lines,
  select several elements (Shift+click or drag a box).
- **Dynamic colours**: "Change with a value…" in an element's properties. Thresholds are entered in
  real units; the editor handles the ×10 scaling and the key colour.
- **Preview** for 107 devices (screen size and font sizes), night mode, sample values.
- **Layout string for device**: copy it and paste it into *Default layout string* in the data field's
  settings in Garmin Connect or Garmin Express.
- **Open / Save XML** in the HMs DIY Designer format (`<DIYLayout>`). A layout string can also be
  pasted into the Open dialog to load an existing layout back. Work is kept in the browser too.

## Layout string

The string is the generation "C" format of HMs DIY Designer 3.4.2: a letter, then four 32-bit
words per element written as base-85, followed by the element's text. The bit layout is
documented above `encodeLayout` in `index.html` and mirrored in `tools/layout_string.py`.

How it was checked:

- The encoder reproduces, character for character, the four Designer-generated strings published
  with their XML in pull request #2 of the Designer repository (Edge 1040 layouts, up to 4984 characters).
- Those four cover text, lines, filled rectangles, circles, arcs and dynamic colours. The remaining
  element kinds (frames, progress bars, filling arcs, direction markers, graphs) follow the
  Designer's own packing code but have no published sample to compare with.
- It has not been tried on a device. If the data field shows "Incompatible string!", it expects a
  different generation than "C".

## Known limits

- Glyph shapes are approximations, because Garmin does not publish its device fonts. Graphic
  elements are positioned exactly.
- Value types are those of Designer 3.4.2. Types added later are unknown; unknown codes found in a
  file are kept in the XML but encoded without a value.
- The font index in the string assumes the standard Garmin order; this could differ on the few
  devices that lack one of the standard sizes.

## Development

    python3 tools/gen_devices.py /path/to/fonts.txt      # device and font table
    python3 tools/layout_string.py layout.xml            # reference encoder
    python3 tools/layout_string.py --check DIR           # verify *_config_string.txt against XML

`tools/types.json` holds the value and graphic types (code, internal id, name, default format,
sample, memory class) taken from Designer 3.4.2.

Designer, examples and manuals: https://github.com/hundsmiachn/Garmin_HMsDIY
