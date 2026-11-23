# HMs DIY Editor

A browser-based layout designer for the Garmin Connect IQ data field **HMs DIY**
(a freely buildable data field by hundsmiachn). The original Designer is Windows-only;
this editor runs anywhere, reads and writes the same XML layouts, and produces the
**layout string** that goes into the data field's settings.

## Use

Open `index.html` in a browser. It is a single file with no build step. Work is kept in the
browser between visits.

### Starting a layout

**New layout** (menu) has three parts side by side:

1. **Device**: a searchable list.
2. **Field**: the screen, or one of the device's field sizes (each size is listed once) for a
   DIY field that sits beside native Garmin fields.
3. **Grid** inside the field: for the screen the device's own data screen layouts. For a smaller
   field up to eight grid ideas (no cell taller than wide), plus **Custom**: a mesh of equal cells
   (each at least 61 × 31 px) in which you merge cells by dragging across them; a click splits a
   merged cell again. Where the mesh is so small that only a handful of grids are possible, all
   of them are listed instead of Custom. The dividing lines are drawn for you, optionally with a
   sample label and value in every cell.

Device and field can be changed later from the top bar. A factory field has a fixed size; only
"Custom size" in the device list lets you type a width and height.

For 178 of the 180 devices the layouts and field rectangles are Garmin's own, taken from the
Connect IQ device files. The two without data (Forerunner 45, vívolife) use an even split.

### Tools

Pick a tool, then **drag on the screen**: the dragged box sets the element's size. A plain click
places nothing. The tool stays active for the next element; **Space**, **Esc** or the **Select**
tool returns to the pointer.

- **Data**: Value, Gauge arc, Progress bar, Graph, Direction.
- **Shapes and text**: Label, Line, Frame, Rectangle, Circle, Disc, Arc.
- **Composite**: ready-made combinations (label + value, now / avg / max, value + unit, framed
  field, dial, gauge, graph or bar with a value). They are scaled into the dragged box and placed
  as a group.
- **Line**: drag for a free line, Shift+drag for a horizontal or vertical one, Ctrl/Cmd+drag to
  span from the nearest line or screen edge to the next one in the drag direction, double-click
  for a full-width horizontal line.

Text sizes are stepped, because a device only has a handful of fonts: a dragged Value or Label
gets the largest font of its family that fits the box.

### Editing

- **On the screen**: drag to move, use the handles to resize, type position and size into the
  badges next to the selected element. Elements snap to each other and to the centre lines.
  Select several with Shift+click or by dragging a box.
- **Grid lines**: a line whose ends touch other lines or the screen edge moves parallel to itself,
  and the lines attached to it grow or shrink with it.
- **Groups**: select layers and press Ctrl/Cmd+G. Clicking a member on the screen selects and
  moves the whole group; a second click selects the single element. A group can be renamed,
  collapsed, locked, hidden, moved or deleted as a whole. In Designer XML a group is written as a
  separator.
- **Properties**: value, format, decimals, sample, font and colour of the selected element. The
  value picker only offers values that make sense for the element.
- **Colour rules**: any element's colour can follow a numeric value ("By value"). Thresholds are
  entered in real units; the editor handles the ×10 scaling and the key colour. A rule can be
  shared by several elements and is then edited in its own panel, reachable from the
  "Colour rules" group at the bottom of the layer list. Filling elements (gauge arc, progress
  bar) take their range from the rule.
- **Night colours**: "Invert at night" per element; the swatch shows the day and night colour.
- **Preview strip** under the canvas (the Preview button hides it): the layout on the device's
  screen, side by side for every position a field of this size has in Garmin's data screen
  layouts, following every change; a round screen shows what the bezel cuts off. With the diagonal of your
  own display entered, the device is drawn at its real physical size. The device's pixel density
  comes from the Connect IQ device file where it has one (72 devices), otherwise from the usual
  screen diagonal of that resolution, marked as estimated.
- **Preview** for 180 devices (screen size and font sizes) with sample values: the 106 of the
  HMs DIY Designer plus 74 newer ones known from the Connect IQ SDK (whether HMs DIY runs on
  those is not known here). The device is chosen in a searchable dialog. Devices that are
  identical for the editor (same screen, fonts and field layouts) share one entry in the device
  list (about a hundred entries); a loaded layout keeps its own device name. Changing the
  device offers to rescale the layout to the new screen.

### Getting it onto the device

- **Layout string**: copy it and paste it into *Default layout string* in the data field's
  settings in Garmin Connect or Garmin Express.
- **Save / Open**: the editor's own project file (`.json`, keeps groups, locks, hidden layers and a
  custom screen size) or HMs DIY Designer XML (`<DIYLayout>`). A layout string can also be pasted
  into the Open dialog to load an existing layout back.

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
- It works on a real Edge 830: text, lines, frames, rectangles, circles, discs, arcs, progress bars and
  filling arcs were checked against device screenshots (`tools/calibration`). Graphs and direction
  markers have not been seen on a device yet. If the data field shows "Incompatible string!", it
  expects a different generation than "C".
- The Garmin settings refused to save strings containing a backslash, which is one of the format's
  85 symbols. The string dialog therefore changes offending elements minimally, in the string only:
  a colour one step off, a position or size one pixel off, the averaging count one higher, or the
  other variant of the same font, and lists what it changed. The exported string never contains a
  backslash (checked on the 61 example layouts and 400 random ones).

## Known limits

- Glyph shapes are approximations, because Garmin does not publish its device fonts. Graphic
  elements are positioned exactly.
- Value types are those of Designer 3.4.2. Types added later are unknown; unknown codes found in a
  file are kept in the XML but encoded without a value.
- The font index in the string assumes the standard Garmin order; this could differ on the few
  devices that lack one of the standard sizes.
- Number fonts (`NR_*`) are assumed to hold digits and signs only; the editor warns when other
  characters are used with them.
- The data screen layouts come from the Connect IQ device files as found in a public repository,
  not from Garmin directly, and were not compared with real devices. Garmin's files are known to
  miss a layout on some newer devices.

## Development

    python3 tools/gen_devices.py /path/to/fonts.txt      # device and font table
    python3 tools/gen_sdk_devices.py SDK_DIR --write     # devices the Designer's list lacks
    python3 tools/gen_fields.py DEVICES_DIR --write      # data screen layouts and field sizes
    python3 tools/gen_fontmetrics.py SDK_DIR --write     # real character widths of the device fonts
    python3 tools/layout_string.py layout.xml            # reference encoder
    python3 tools/layout_string.py --check DIR           # verify *_config_string.txt against XML

`gen_fields.py` reads one `simulator.json` per device, as in the `Devices` folder of a Connect IQ
SDK installation, and rewrites the `FIELDS` table in `index.html`. It also reports devices whose
screen size differs from the editor's table.

`gen_fontmetrics.py` reads the SDK's bitmap fonts (`Fonts/*.cft`) and vector fonts (`*.ttf`, scaled
to each device's point size and ppi) and stores only numbers (line height, ascent, glyph height,
character widths), no glyph images. Text in the preview is stretched to these widths.
Devices whose fonts were not available keep the browser's own text measure.

`tools/types.json` holds the value and graphic types (code, internal id, name, default format,
sample, memory class) taken from Designer 3.4.2.

Designer, examples and manuals: https://github.com/hundsmiachn/Garmin_HMsDIY
