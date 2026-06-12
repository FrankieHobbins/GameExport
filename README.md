# GameExport

GameExport is an Advanced Export Addon for Blender 2.8 and onwards. It supports **FBX** and **GLB (glTF Binary)** export formats. Its core feature is the ability to tag collections using symbols, these tags define custom export parameters.


## Export Buttons

**Export:** Exports everything in Scene

**Selected:** Exports only selected Collection

**Bake:** Exports all collections with "_high" or "_low" in collection name

## Export Formats

In the **Settings** panel, use the **Format** dropdown to choose between:

* **FBX** - Default format, supports Unity and Unreal engine-specific export settings
* **GLB** - glTF Binary format, ideal for web rendering, Unity, Unreal, and other modern engines. GLB embeds textures and materials automatically.

## Tags:

```
& - Collection will be merged into a single mesh
* - Collection will be ignored and not exported (Useful for booleans for example)
! - Exclude from Merging
```

## Things to Note

* No symbol on a collection will export each object inside individually

* Any object with origin in the name in the collection sets the origin

* All materials should match the collection name for substance painter to interpret everything correctly.

* Baked stuff going in it's own collection, shares same material though. Offset uvs outside of 0-1 if you don't want the baking to have problems)


## Settings

**Path:** Defines where the object will export to.

**Prefix:** Adds Prefix to exported filenames.

**Scale:** Set Export Scale (Default is 1).

**Engine:** Define if you are using Unreal or Unity. This affects the export transforms. (For Snowdrop use Unity). FBX-only setting.

**Format:** Choose export format - FBX or GLB. GLB is recommended for web-based workflows and modern game engines.

**Center:** Centers objects to world zero for export. When using merge collection tags it will not center your object. To get it to work, make sure you have an empty inside the merge collection with the tag 'origin' this will be the merged objects new origin, it will also then move to world zero (if center is enabled in settings).

