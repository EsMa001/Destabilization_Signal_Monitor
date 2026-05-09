# Design System: Tactical Intelligence & Operations

## 1. Overview & Creative North Star: "The Silent Sentinel"

This design system is built to transform complex global data into actionable intelligence. The **Creative North Star** is "The Silent Sentinel"—an aesthetic that prioritizes cold, clinical precision, extreme information density, and the authoritative weight of a high-level security briefing. 

We are moving away from the "friendly SaaS" look. There are no rounded corners, no soft pill-shaped buttons, and no vibrant decorative colors. Instead, we utilize **Brutalist Precision**: sharp 0px corners, high-contrast typography, and a "HUD" (Heads-Up Display) layout style. The interface should feel like a custom-built hardware terminal where every pixel serves a tactical purpose.

## 2. Colors & Tonal Depth

The palette is rooted in the deep void of global operations, utilizing a "Night Vision" spectrum of charcoal, slate, and emerald.

### Surface Hierarchy & The "No-Line" Rule
Traditional UI relies on borders to separate modules. In this system, we prohibit 1px solid borders for sectioning. Boundaries are defined through **Background Color Shifts**. 
- **Base Layer:** `surface` (#0b1326) represents the foundation.
- **Content Blocks:** Use `surface_container_low` (#131b2e) for primary dashboard widgets.
- **Nested Elements:** Use `surface_container_high` (#222a3d) for interior data modules.
- **Interaction:** Use `surface_bright` (#31394d) only for active hover states or triggered overlays.

### Signature Textures & Glass
To prevent the "flat box" look, we employ **Tactical Glassmorphism**. Floating menus or modal overlays must use `surface_container` at 70% opacity with a `20px` backdrop blur. This allows the high-contrast world map or data streams to bleed through, maintaining the user’s sense of context.

### The "Emerald Pulse"
The `primary` emerald (#51e1a5) is a weaponized color. Use it sparingly for "Active," "Online," or "Secure" states. For CTAs, use a subtle vertical gradient from `primary` (#51e1a5) to `primary_container` (#2ac48b) to give the button a "lit-from-within" hardware glow.

## 3. Typography: Technical Authority

The typography utilizes a "Dual-Font Logic" to separate narrative data from raw technical telemetry.

*   **Primary Sans (Inter):** Used for headlines and body. Inter’s tall x-height provides readability at high density. 
*   **Technical Mono (Space Grotesk):** Used for all `label` and `data` tokens. This conveys a "machine-read" aesthetic, ideal for timestamps, coordinates, and status codes.

**Scale Usage:**
- **Display-LG (3.5rem):** Reserved for critical status metrics (e.g., "THREAT LEVEL: HIGH").
- **Title-SM (1rem):** The workhorse for widget headers. Always uppercase with `0.05em` letter spacing.
- **Label-SM (0.6875rem / Space Grotesk):** Used for metadata, axis labels on charts, and micro-telemetry.

## 4. Elevation & Depth: Tonal Layering

This system rejects shadows. In a world of digital intelligence, shadows represent ambiguity. We achieve depth through **Physical Stacking**.

*   **The Layering Principle:** Higher-priority information sits on a "higher" surface token. A `surface_container_highest` card sitting on a `surface` background provides enough contrast to be perceived as elevated without the need for a drop shadow.
*   **The "Ghost Border" Fallback:** If high-density data requires containment, use a "Ghost Border." Apply `outline_variant` (#3c4a3c) at **15% opacity**. This creates a microscopic edge that guides the eye without cluttering the visual field.
*   **Active Glow:** Instead of a shadow, an active element (like a selected node on a map) should have a soft, 8% opacity `primary` glow to mimic an illuminated screen.

## 5. Components

### Buttons: Tactical Trigger
- **Primary:** Sharp 0px corners. Background: `primary`. Text: `on_primary` (all caps, Bold).
- **Secondary:** Ghost variant. `outline` border at 20% opacity. No fill. Text: `primary`.
- **States:** On hover, the button should not grow; it should "invert"—the fill becomes `primary_fixed_dim` and text stays sharp.

### Inputs: Data Entry
- **Text Fields:** Minimalist. Only a bottom border (1px) using `outline`. When focused, the border transitions to `primary` with a subtle `primary_container` glow.
- **Labels:** Always `label-sm` (Space Grotesk) positioned above the field, never floating inside.

### Cards & Modules
- **Rule:** Absolute prohibition of divider lines. 
- **Separation:** Use 24px of vertical whitespace or a shift from `surface_container_low` to `surface_container_lowest`.
- **Header:** Headers should be separated from content by a 2px tall, 16px wide horizontal bar of `primary` emerald in the top-left corner.

### Data Visualization
- **Charts:** Use `primary` for healthy data, `tertiary` (#8ed0ff) for secondary streams, and `error` (#ffb4ab) for anomalies. 
- **The Map:** The high-contrast world map must use `background` for water and `surface_container_highest` for landmasses. Points of interest use `primary` with a "pulse" animation.

## 6. Do’s and Don’ts

### Do:
- **Do** use `Space Grotesk` for all numerical data and timestamps.
- **Do** lean into asymmetry. A sidebar that doesn't span the full height or a widget that breaks the grid creates a bespoke, "custom-engineered" feel.
- **Do** use high-contrast "Interstate" style iconography—thin strokes, no fills.

### Don't:
- **Don't** use border-radius. Every corner in this system must be `0px`.
- **Don't** use standard "Grey" for text. Use `on_surface_variant` (#bbcbb8) for a slightly tinted, military-grade legibility.
- **Don't** use standard "Drop Shadows." If you must elevate, use tonal shifts or 4-8% opacity ambient glows.
- **Don't** clutter the screen with dividers. Let the background color shifts do the heavy lifting.