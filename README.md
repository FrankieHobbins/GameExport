# GameExport

GameExport is an FBX Export Addon for Blender 2.8 and onwards. It's core feature is the ability to tag collections using symbols, these tags define custom export parameters. 


## Export Buttons

**Export:** Exports everything in Scene

**Selected:** Exports only selected Collection

**Bake:** Exports all collections with "_high" or "_low" in collection name

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

* Baked stuff going in it’s own collection, shares same material though. Offset uvs outside of 0-1 if you don’t want the baking to have problems)


## Settings

Path: Defines where the object will export to.

Prefix: Adds Prefix

Scale: Set Export Scale (Default is 1).

Engine: Define if you are using Unreal of Unity. This is affect the export transforms. (For Snowdrop use Unity)

