# Runtime verification of Displays, without an operator at the screen

A clean build proves bindings compile; it does not prove the screen behaves. This is the recipe for an AI to
test a Display's dynamics in the running RichClient using only the FrameworX AI Designer MCP, and the list of
what still needs a human. Proven in a real project: 18 runtime checks found 4 defects that design-time
screenshots had passed.

Companion docs: `Verification-Channels-and-Simulators.md` (which channel proves what), the `run-tests` skill
(structural + live gates), the `commission-the-points` skill (per-point evidence).

## 1. One-time setup per solution

- `DisplaysClientSettings.StartMaximized = true`: the blank template starts un-maximized and runtime
  captures come out tiny (675×355).
- Runtime on the **Development** profile, RichClient (`designer_action('start_runtime','richclient')`):
  runtime screenshots only work on the WPF RichClient.

## 2. The loop, per display

1. **Point the client at the display.** The MCP has no verb to open a display in the running client
   (`Display.X.Open()` is a method; `set_object_value` cannot call it). So: read the `Startup` layout
   (`get_objects('DisplaysLayouts', detail='full', names=['Startup'])`), set the Content member `Page` to
   `Display.<Name>`, and write the whole document back.
2. **Build** (`designer_action('build')`). Skipping it starts the runtime on the stale layout.
3. **Start the runtime.** `start_runtime` can return `RUNTIME_NOT_BOUND` while the runtime is still booting.
   Do not retry the start; wait about 15 s and poll `get_state(target='runtime')` until
   `runtimeConnected: true`.
4. **Drive the state** with `set_object_value(path='Tag.<path>', value='...')`. Tag values are not retentive
   across runtime restarts, so set them after every start.
5. **Capture.** `get_screenshot(target='runtime', max_width=0)`; if the first capture after a start times
   out, retry once. Read the image.
6. **Record** expected vs seen per check in `Sites/<Name>/Tests/<phase>-runtime-verify-<date>.md`, with the
   screenshot file names.
7. Stop the runtime before the next import (`designer_action('stop_runtime')`).

## 3. Designing the checks (what to drive)

| Dynamic / element | Drive | Proves |
|---|---|---|
| Multi-state visibility table (OFF / ON / OSC / OFF-ON) | each value in turn | the visibility **direction**: with show-when-true exactly one state shows per value; inverted, three would show |
| Rotation (needle) | min, mid, max, a non-round value (4.25, 10.5) | pivot and angle mapping. A display that renders tiny in a corner means an element transformed far off-canvas: suspect the pivot |
| Colour thresholds | a value per threshold | limit order and colours |
| Formatted numbers | a value with decimals and one of 1,000 or more | format string (`F0` vs `N0` separator), rounding, mask prefixes/suffixes |
| Text values | a long string | clipping inside the field width |
| Date / time | nothing, just look | one line, no wrapped time part |
| Blinking / timer-driven states | two captures about 1 s apart | the driving task runs (red at t, green at t+1) |
| Bargraph | min / mid / max | direction and fill |

Pick states that make a wrong mapping **visibly** wrong (non-round values, mutually exclusive states), not
values that pass by coincidence (0 and 100).

## 4. Evidence

- Don't take the timestamp from the `set_object_value` echo. Read `Timestamp` and `Quality` with
  `browse_object_model('Tag.<path>')` for the commissioning-style evidence row.
- Keep the screenshot paths in the record; they are the proof.

## 5. What still needs a human (say it plainly in the record)

- Clicks: momentary pushbuttons (down/up), toggles, smart buttons writing values, code-behind commands.
- Keypad / TextBox entry writing back to the tag.
- Navigation between displays.
- Comparison against the source drawing or the previous screen, where the intended behavior is ambiguous
  (for example, whether an icon blinks).

List these as "not tested" rows, never as passes.
