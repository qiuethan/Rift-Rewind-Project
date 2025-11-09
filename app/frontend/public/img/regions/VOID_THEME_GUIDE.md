# The Void - Theme Guide

## Color Palette

### Primary Colors
- **Primary Purple**: `#A855F7` - Main void energy color (violet-500)
- **Secondary Dark**: `#0A0118` - Deep void darkness
- **Accent Lavender**: `#C084FC` - Lighter void energy (violet-400)

### Text Colors
- **Text Primary**: `#F3E8FF` - Lightest purple (violet-50)
- **Text Secondary**: `#D8B4FE` - Medium light purple (violet-300)
- **Text Dim**: `#A78BFA` - Dimmed purple (violet-400)

### Background
- **Gradient**: `radial-gradient(ellipse at center, #1A0B2E 0%, #0A0118 60%, #000000 100%)`
  - Creates a cosmic void effect radiating from center to pure black

### UI Elements
- **Panel Background**: `rgba(168, 85, 247, 0.08)` - Subtle purple tint
- **Panel Border**: `rgba(168, 85, 247, 0.35)` - Visible purple border
- **Panel Hover**: `rgba(168, 85, 247, 0.12)` - Slightly brighter on hover

### Status Colors
- **Danger**: `#DC2626` - Red for errors (red-600)
- **Success**: `#A855F7` - Primary purple for success
- **Warning**: `#C084FC` - Accent lavender for warnings

### Shadows & Glows
- **Primary Shadow**: `0 0 30px rgba(168, 85, 247, 0.4)` - Strong void glow
- **Secondary Shadow**: `0 0 50px rgba(192, 132, 252, 0.3)` - Softer accent glow
- **Inner Glow**: `inset 0 0 25px rgba(168, 85, 247, 0.15)` - Subtle inner void energy

## Design Philosophy

The Void theme embodies:
- **Cosmic Horror**: Deep space darkness with unnatural purple void energy
- **Otherworldly**: Colors that feel alien and unsettling
- **Hunger**: Pulsing glows suggesting consuming void creatures
- **Mystery**: Dark backgrounds with ethereal purple highlights

## Usage in Components

### Graphs & Charts
- Use `#A855F7` for primary data lines
- Use `#C084FC` for secondary/comparison data
- Background should be dark with subtle void glow effects

### Buttons & Interactive Elements
- Primary buttons: `#A855F7` background with `#F3E8FF` text
- Hover state: Increase glow intensity
- Active state: Darken to `#9333EA` (violet-600)

### Cards & Panels
- Semi-transparent purple backgrounds
- Purple borders with glow effects
- Dark interior with void pattern overlay

### Text Hierarchy
1. Headers: `#F3E8FF` (brightest)
2. Body: `#D8B4FE` (medium)
3. Captions: `#A78BFA` (dimmed)

## Assets

- **Hero Image**: `/img/regions/void-hero.jpg` (paste your background here)
- **Background**: `/img/regions/void-bg.jpg` (paste your background here)
- **Pattern SVG**: `/img/regions/void-pattern.svg` ✅ Created
- **Decorative SVG**: `/img/regions/void-eye.svg` ✅ Created
- **Particles**: `/particles/void-tendrils.webm` (optional animated tendrils)

## Tagline
**"Hunger without end."**

---

## Implementation Notes

The theme is now registered in `runeterraThemes.ts` and will:
- Automatically apply to Void champions (Kassadin, Malzahar, Kha'Zix, Rek'Sai, Vel'Koz, Cho'Gath, Kog'Maw, Kai'Sa, Bel'Veth)
- Be available in the random theme rotation
- Apply consistent void aesthetics across all pages and components
