# Bruno Simon folio-2019 — feature inventory vs Mark's World

Source read line by line: `src/javascript/**` (54 files). Legend: ✅ meron na tayo · 🟡 partial · ❌ wala pa.

## 1. Engine / loop
| Bruno | Paano niya ginawa | Atin |
|---|---|---|
| Time / Sizes / Resources | EventEmitter classes; `tick` event; loader w/ progress → starting screen | ✅ (rAF loop + THREE.DefaultLoadingManager) |
| Starting screen | 3D "loading" label sa floor, floor border fills with progress, then "START" area; press Enter/click → `reveal.go()` | 🟡 HTML card lang tayo (ok), walang 3D reveal |
| Reveal | matcap reveal shader 3s, floor shadows fade in, **car drops from z=12**, engine sound fades in, `reveal` sound | ❌ → gagawin: rider drops from the sky + dust + chime |
| Post-processing | Blur passes (off on touch / in projects zone), Glow pass (pink vignette) | ❌ skip (perf); CSS gradient background instead |
| Title bar | `document.title` = `____🚗___` na gumagalaw ayon sa speed, every 300 ms | ❌ → gagawin (🐕) |
| visibilitychange | reset lahat ng key actions pag balik ng tab | ❌ → gagawin |
| Debug | `#debug` hash → dat.gui, physics wireframes | ❌ (may `?mgdebug` sa main site lang) |

## 2. Camera (`Camera.js`)
| Bruno | Atin |
|---|---|
| Fixed angle vector `default (1.135,-1.45,1.15)`; `projects (0.38,-1.4,1.63)` mas top-down; gsap 2 s transition pag pumasok sa projects zone | 🟡 fixed lang → gagawin: per-zone angle na naka-lerp |
| target eased 0.15/frame | ✅ (dt*3.5) + look-ahead (wala kay Bruno) |
| zoom: wheel 14–29, pinch on touch, eased 0.1 | 🟡 wheel lang → gagawin: pinch |
| **pan**: mouse drag / 1-finger drag raycast sa plane, eased, reset pag nag-drive | ❌ → gagawin |
| cursor classes grab/grabbing/pointer | ❌ → gagawin |

## 3. Physics (`Physics.js`, cannon.js)
| Bruno | Atin |
|---|---|
| World gravity -13, allowSleep, contact materials floor/dummy/wheel | kinematic (walang engine) — sinadya, `ponytail:` |
| RaycastVehicle: 4 wheels, suspension 50 stiffness, frictionSlip 10, chassis mass 40 | rider velocity ease; ✅ screen-relative (mas madali kaysa car-relative) |
| steering eased (`controlsSteeringSpeed`), max PI*0.17, quad steering option | ✅ heading ease |
| accelerate/boost/brake; slow-down impulse pag walang input | ✅ (Shift boost, decel) |
| upside-down auto-flip after 1 s | N/A |
| `jump()` impulse (ginagamit sa flip at klaxon hop) | ✅ Space |
| `addObjectFromThree`: collision.glb shapes (cube/cylinder/sphere/center) → body; sleep; `reset()` | 🟡 circles lang; ❌ reset → gagawin (reset pads, bounce/height) |
| collide event → sound w/ impact velocity | 🟡 blip kapag push>3.5 |

## 4. Car (`Car.js`)
| Bruno | Atin |
|---|---|
| chassis/wheels glb (matcap) | ✅ low-poly Kimpoy+Dianna, umiikot sa heading |
| **antenna spring** (secondary motion mula sa acceleration) | ❌ → gagawin: buhok ni Dianna + tenga ni Kimpoy |
| back lights: brake red, reverse yellow | ❌ → tongue out pag boost |
| screech sound sa biglang accel; engine sound rate/volume = speed+accel | 🟡 gallop thuds |
| klaxon `H` (horn + hop), `K` rain of horns, `B` shoot balls (cybertruck) | ❌ → `H` = bark + hop + "Woof!" |
| TransformControls debug | ❌ |

## 5. World objects
| Bruno | Atin |
|---|---|
| `Objects.add({base, collision, mass, shadow, soundName, sleep})` | 🟡 `addProp(kind)` |
| Fake **shadows**: plane per object, offset by sun vector × height, alpha by height & orientation | 🟡 rider lang → gagawin: blob shadow sa bawat prop |
| Static merge (BufferGeometryUtils) for draw calls | ❌ → InstancedMesh para sa path stones |
| Matcap materials + indirect bounce light from floor + reveal | flat-shaded Phong (ok na sa style) |
| Floor: 4-corner gradient; baked floor-shadow PNG per section | ❌ → CSS gradient bg |
| **Tiles** (path stones between sections, random model, alternating tangent offset, rotation index) | ❌ → gagawin: stone paths Manila → bawat landmark |
| **Walls** builder: rectangle / brick / triangle; random rotation | ❌ → gagawin: brick wall + pins triangle |

## 6. Areas & Zones (`Area.js`, `Zones.js`)
| Bruno | Atin |
|---|---|
| Area = floor border + **fence na tumataas** pag pumasok (gsap back.out), `ENTER` key label lumilitaw, hover ng mouse nag-a-activate din, click/Enter/E/F = interact → callback (open link / reset / wig) + `uiArea` sound | 🟡 zones lang (auto-open panel) → gagawin: interact pads para sa project links, contact links, reset |
| Zones (rect): `in`/`out` events → camera angle + blur | ✅ circles (auto panel) |

## 7. Sections
| Bruno | Atin |
|---|---|
| Intro: **BRUNO SIMON** letters = pushable bodies; arrow-key blocks; instructions labels; brick dikes | ✅ MARK blocks; ❌ dikes/arrow keys |
| Crossroads: static + tiles sa 3 direksyon | 🟡 signpost lang → paths |
| Projects: boards w/ slides, floor label, distinctions trophies (pushable), **OPEN** area = link | 🟡 boards + panel → gagawin OPEN pads |
| Information: contact areas (Twitter/GitHub/LinkedIn/Mail), baguettes pushable, activities image | 🟡 panel lang → contact pads |
| Playground: brick walls ×3 (rect/brick/triangle), bowling pins triangle + ball, **reset** areas | 🟡 pins+ball; ❌ walls, reset |
| EasterEggs: **Konami** (lemon rain 3^n), wigs area (0,80), eggs w/ codes | ❌ → Konami = coconut rain |

## 8. Controls (`Controls.js`)
| Bruno | Atin |
|---|---|
| keyboard WASD/arrows, Ctrl/Space brake, Shift boost, R reset | ✅ (Space = jump sa atin) |
| touch: joystick (angle relative sa car, log radius), boost/forward/brake/backward buttons, reveal after start | ✅ joystick (screen-relative) + JUMP |
| gamepad | ✅ (wala kay Bruno 2019) |

## 9. Sounds (`Sounds.js`, Howler)
| Bruno | Atin |
|---|---|
| engine loop: rate 0.4–1.4 & volume by speed/accel, easing up .3 down .15 | 🟡 thuds per step |
| brick/bowling/carHit/woodHit/screech/uiArea/horns/reveal; minDelta, velocity→volume², random rate | 🟡 synth blips |
| `M` mute; mute pag hidden tab | ✅ `L` mute; ❌ hidden-tab mute → gagawin |

## Takeaways na inabsorb
1. **Orientation reads direction** — 3D body na umiikot, hindi sprite. (Naayos na.)
2. **Secondary motion** (antenna) ang nagbibigay ng "buhay". → buhok/tenga spring.
3. **Paths/tiles** ang gabay ng bisita; walang minimap si Bruno, tiles ang nagtuturo.
4. **Areas na may fence + ENTER** ang pattern ng interaction, hindi auto-popup.
5. **Fake shadows + matcap + floor gradient** ang look, hindi real lighting.
6. Lahat ng physics object ay may `reset()`; may reset pads sa playground.
7. Sound = velocity-scaled, may minDelta para hindi mag-spam.
8. Easter eggs (Konami, H horn, K rain) = personality.
