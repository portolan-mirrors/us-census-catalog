// The copy button's label per state. Pure; tested by about.test.mjs.

const LABELS = { idle: "Copy", done: "Copied", fail: "Press ⌘C" };

/** The button label for a copy state. Unknown states fall back to idle. */
export function copyLabel(state) {
  return LABELS[state] ?? LABELS.idle;
}
