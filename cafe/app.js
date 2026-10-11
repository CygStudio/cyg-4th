import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const $ = (id) => document.getElementById(id);
const canvas = $('scene');
const host = canvas.parentElement;
const dialog = $('research-dialog');
for (const id of ['open-research', 'open-research-bottom']) $(id).addEventListener('click', () => dialog.showModal());
$('close-research').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
$('retry').addEventListener('click', () => location.reload());

const views = {
  overview: { title: '整體剖面', position: [8.4, 8.9, 11.4], target: [-.4, .8, -.2], note: '一張公開照片，立起一個空間', text: '主座位區依場租照片重建。吧台與外廊參考較早照片補足，位置與尺寸仍為推估。', cutaway: true },
  interior: { title: '中央長桌', position: [.40, 1.80, 3.12], target: [.05, 1.05, -1.35], note: '長桌，是這張照片的中心', text: '以中央長桌、兩側座位與後方投影幕為主要結構。保留照片裡的空間關係，精確尺度仍待丈量。', cutaway: false },
  window: { title: '窗邊座位', position: [1.05, 1.82, .1], target: [-2.83, 1.30, -.6], note: '一排窗，接住室外的光', text: '黑色窗框與四盞吊燈可在場租照中辨認。外廊依早期照片補足，現況與深度尚未確認。', cutaway: false },
  counter: { title: '吧台一角', position: [.05, 1.8, .55], target: [.15, 1.40, 4.53], note: '這一角，留著歷史的參考', text: '藍框黑板、咖啡機與點餐吧台來自 2018 年實拍。這裡不是已核實的現況，與主座位區的接合亦為推估。', cutaway: false },
  plan: { title: '俯看配置', position: [-.5, 17.5, .01], target: [-.5, .25, 0], note: '俯看關係，不當作丈量圖', text: '桌椅與主要區域可用來討論空間感。所有尺寸與間距均為推估；洗手間及未拍到的後場沒有建立。', cutaway: true },
};
const state = { ready: false, view: 'overview', cutaway: true, outline: true, evidence: false, quality: 'balanced', daylight: 1, frameCount: 0, intersecting: true, disposed: false, frames: [] };
const resources = { geometries: new Set(), materials: new Set(), textures: new Set() };
let renderer, scene, camera, controls, room, frameId = 0, startedAt = performance.now();
const sourceMeshes = [], lineMeshes = [], materialPairs = new Map();
const controller = new AbortController();
const { signal } = controller;
const ramp = new THREE.DataTexture(new Uint8Array([90, 175, 255]), 3, 1, THREE.RedFormat);
ramp.minFilter = ramp.magFilter = THREE.NearestFilter;
ramp.generateMipmaps = false; ramp.needsUpdate = true;
resources.textures.add(ramp);

function render() {
  frameId = 0;
  if (!state.ready || state.disposed || document.hidden || !state.intersecting) return;
  const begin = performance.now();
  renderer.render(scene, camera);
  state.frameCount++;
  if (state.frames.length === 240) state.frames.shift();
  state.frames.push(performance.now() - begin);
}
function invalidate() {
  if (state.ready && !frameId && !state.disposed && !document.hidden && state.intersecting) frameId = requestAnimationFrame(render);
}
function applyQuality() {
  renderer.setPixelRatio(state.quality === 'light' ? 1 : Math.min(devicePixelRatio || 1, 1.6));
  renderer.setSize(host.clientWidth, host.clientHeight, false);
  invalidate();
}
function resize() {
  if (!renderer || state.disposed) return;
  camera.aspect = host.clientWidth / host.clientHeight;
  camera.updateProjectionMatrix(); applyQuality();
  if (state.ready && ['overview', 'plan'].includes(state.view)) setView(state.view);
}
function updateVisibility() {
  for (const mesh of sourceMeshes) {
    const zone = mesh.userData.zone;
    mesh.visible = zone === 'roof' ? !state.cutaway : ['shell', 'tilewall'].includes(zone) ? !state.cutaway : true;
    mesh.material = state.evidence && ['historic', 'patio'].includes(zone) ? materialPairs.get(mesh).inferred : materialPairs.get(mesh).toon;
  }
  for (const line of lineMeshes) line.visible = state.outline;
  $('cutaway').setAttribute('aria-pressed', String(state.cutaway));
  $('outline').setAttribute('aria-pressed', String(state.outline));
  $('evidence').setAttribute('aria-pressed', String(state.evidence));
  $('gesture').textContent = state.evidence ? '橘色：歷史參考補足區；全區尺寸皆推估' : '拖曳旋轉 · 雙指縮放';
  invalidate();
}
function setView(name) {
  const view = views[name];
  if (!view || !state.ready) return;
  state.view = name; state.cutaway = view.cutaway;
  camera.fov = ['overview', 'plan'].includes(name) ? 39 : name === 'interior' ? 68 : 56;
  camera.updateProjectionMatrix();
  controls.target.fromArray(view.target); camera.position.fromArray(view.position);
  // Fit the same room to a narrow viewport without cropping the cutaway.
  if (name === 'overview' || name === 'plan') {
    const fit = Math.max(1, 1.22 / camera.aspect);
    camera.position.sub(controls.target).multiplyScalar(fit).add(controls.target);
    controls.maxDistance = 48; controls.minDistance = 4;
  } else { controls.minDistance = .6; controls.maxDistance = 14; }
  controls.maxPolarAngle = Math.PI * .49;
  camera.lookAt(controls.target); controls.update();
  for (const button of document.querySelectorAll('[data-view]')) button.setAttribute('aria-pressed', String(button.dataset.view === name));
  $('view-label').textContent = view.title;
  $('note-title').textContent = view.note;
  $('note-body').textContent = view.text;
  updateVisibility();
}
function zoom(factor) {
  if (!state.ready) return;
  const offset = camera.position.clone().sub(controls.target);
  offset.setLength(THREE.MathUtils.clamp(offset.length() * factor, controls.minDistance, controls.maxDistance));
  camera.position.copy(controls.target).add(offset); controls.update(); invalidate();
}
function fail(error) {
  console.error('Cafe viewer:', error);
  state.ready = false;
  $('loading').hidden = true; $('error-panel').hidden = false;
  $('fallback').classList.remove('hidden'); canvas.classList.remove('ready');
  $('model-status').textContent = '目前顯示空間預覽';
  for (const element of document.querySelectorAll('[data-view], .toolbar button, .toolbar input, .toolbar select, .zoom-controls button')) element.disabled = true;
}

async function init() {
  renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NoToneMapping;
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(39, 1, .07, 120);
  controls = new OrbitControls(camera, canvas);
  controls.enableDamping = false; controls.enablePan = false; controls.rotateSpeed = .65; controls.zoomSpeed = .85;
  controls.addEventListener('change', invalidate);
  scene.add(new THREE.HemisphereLight(0xfff4df, 0x9dafa9, 1.5));
  const sun = new THREE.DirectionalLight(0xfff4dc, 2.05); sun.position.set(-5, 7, 2); scene.add(sun);
  const fill = new THREE.DirectionalLight(0xc5d7ea, .45); fill.position.set(3, 4, -3); scene.add(fill);
  // Contact disc under the plinth, generated locally; no remote textures or photograph reuse.
  const shadowCanvas = document.createElement('canvas'); shadowCanvas.width = shadowCanvas.height = 128;
  const context = shadowCanvas.getContext('2d'); const gradient = context.createRadialGradient(64, 64, 18, 64, 64, 64);
  gradient.addColorStop(0, 'rgba(42,65,44,.24)'); gradient.addColorStop(1, 'rgba(42,65,44,0)'); context.fillStyle = gradient; context.fillRect(0, 0, 128, 128);
  const contactTexture = new THREE.CanvasTexture(shadowCanvas); resources.textures.add(contactTexture);
  const contactMaterial = new THREE.MeshBasicMaterial({ map: contactTexture, transparent: true, depthWrite: false }); resources.materials.add(contactMaterial);
  const contactGeometry = new THREE.PlaneGeometry(12, 14); resources.geometries.add(contactGeometry);
  const contact = new THREE.Mesh(contactGeometry, contactMaterial); contact.rotation.x = -Math.PI / 2; contact.position.set(-.5, -.02, 0); scene.add(contact);
  resize();
  const response = await fetch('assets/little-donkey.glb', { signal });
  if (!response.ok) throw new Error(`GLB HTTP ${response.status}`);
  const bytes = await response.arrayBuffer();
  if (state.disposed) return;
  const gltf = await new GLTFLoader().parseAsync(bytes, new URL('assets/', location.href).href);
  if (state.disposed) { gltf.scene.traverse((o) => { if (o.isMesh) { o.geometry.dispose(); for (const m of Array.isArray(o.material) ? o.material : [o.material]) m.dispose(); } }); return; }
  room = gltf.scene;
  const toons = new Map(), inferred = new Map(), originals = new Set();
  const ink = new THREE.LineBasicMaterial({ color: 0x42413b, transparent: true, opacity: .48 }); resources.materials.add(ink);
  room.traverse((mesh) => {
    if (!mesh.isMesh) return;
    resources.geometries.add(mesh.geometry);
    const original = mesh.material; originals.add(original);
    if (!toons.has(original.uuid)) {
      const toon = new THREE.MeshToonMaterial({ color: original.color.clone(), gradientMap: ramp, side: THREE.FrontSide });
      const highlight = new THREE.MeshToonMaterial({ color: 0xd28a39, gradientMap: ramp });
      // A restrained unlit contribution keeps the inside legible without expensive shadow maps.
      toon.emissive.copy(original.color).multiplyScalar(.09);
      toons.set(original.uuid, toon); inferred.set(original.uuid, highlight);
      resources.materials.add(toon); resources.materials.add(highlight);
    }
    materialPairs.set(mesh, { toon: toons.get(original.uuid), inferred: inferred.get(original.uuid) });
    mesh.material = toons.get(original.uuid); sourceMeshes.push(mesh);
  });
  // Add edges after traversal so new children never enter the material pass.
  for (const mesh of sourceMeshes) {
    if (mesh.userData.zone === 'roof') continue;
    const edge = new THREE.EdgesGeometry(mesh.geometry, 38); resources.geometries.add(edge);
    const line = new THREE.LineSegments(edge, ink); line.renderOrder = 1;
    mesh.add(line); lineMeshes.push(line);
  }
  for (const material of originals) material.dispose();
  scene.add(room); state.ready = true;
  for (const element of document.querySelectorAll('[data-view], .toolbar button, .toolbar input, .toolbar select, .zoom-controls button')) element.disabled = false;
  const initialView = new URLSearchParams(location.search).get('view');
  setView(views[initialView] ? initialView : 'overview'); render();
  state.firstFrameMs = Math.round(performance.now() - startedAt); state.modelBytes = bytes.byteLength;
  $('loading').hidden = true; $('fallback').classList.add('hidden'); canvas.classList.add('ready');
  $('model-status').textContent = `模型 ${(bytes.byteLength / 1e6).toFixed(2)} MB · 拖曳查看`;
  for (const button of document.querySelectorAll('[data-view]')) button.addEventListener('click', () => { setView(button.dataset.view); if (matchMedia('(max-width:700px)').matches) host.scrollIntoView({ block: 'start', behavior: 'instant' }); }, { signal });
  $('cutaway').addEventListener('click', () => { state.cutaway = !state.cutaway; updateVisibility(); }, { signal });
  $('outline').addEventListener('click', () => { state.outline = !state.outline; updateVisibility(); }, { signal });
  $('evidence').addEventListener('click', () => { state.evidence = !state.evidence; updateVisibility(); }, { signal });
  $('quality').addEventListener('change', () => { state.quality = $('quality').value; applyQuality(); }, { signal });
  $('daylight').addEventListener('input', () => { state.daylight = Number($('daylight').value); sun.intensity = state.daylight * 2.05; invalidate(); }, { signal });
  $('zoom-in').addEventListener('click', () => zoom(.85), { signal });
  $('zoom-out').addEventListener('click', () => zoom(1.18), { signal });
  $('reset').addEventListener('click', () => setView('overview'), { signal });
  canvas.addEventListener('keydown', (event) => {
    if (event.key.toLowerCase() === 'r') { event.preventDefault(); setView('overview'); return; }
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '-', '='].includes(event.key)) return;
    event.preventDefault();
    if (['+', '='].includes(event.key)) return zoom(.85);
    if (event.key === '-') return zoom(1.18);
    const spherical = new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
    spherical.theta += event.key === 'ArrowLeft' ? -.12 : event.key === 'ArrowRight' ? .12 : 0;
    spherical.phi = THREE.MathUtils.clamp(spherical.phi + (event.key === 'ArrowUp' ? -.1 : event.key === 'ArrowDown' ? .1 : 0), .06, Math.PI * .49);
    camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical)); controls.update(); invalidate();
  }, { signal });
}
const observer = new ResizeObserver(resize); observer.observe(host);
const visibilityObserver = new IntersectionObserver(([entry]) => { state.intersecting = entry.isIntersecting; invalidate(); }, { threshold: 0 }); visibilityObserver.observe(host);
document.addEventListener('visibilitychange', invalidate, { signal });
canvas.addEventListener('webglcontextlost', (event) => { event.preventDefault(); fail(new Error('WebGL context lost')); }, { signal });
function dispose() {
  state.disposed = true; state.ready = false; controller.abort(); cancelAnimationFrame(frameId);
  observer.disconnect(); visibilityObserver.disconnect(); controls?.dispose();
  for (const resource of resources.geometries) resource.dispose();
  for (const resource of resources.materials) resource.dispose();
  for (const resource of resources.textures) resource.dispose();
  renderer?.dispose();
}
window.addEventListener('pagehide', (event) => { if (!event.persisted) dispose(); });
window.addEventListener('pageshow', (event) => { if (event.persisted) { resize(); invalidate(); } });
// Read-only diagnostic snapshot for browser QA; metrics are not a physical-device FPS claim.
window.__cafe = { get ready() { return state.ready; }, snapshot() { return { ...state, frames: [...state.frames], renderer: renderer ? { calls: renderer.info.render.calls, triangles: renderer.info.render.triangles, lines: renderer.info.render.lines, geometries: renderer.info.memory.geometries, textures: renderer.info.memory.textures, dpr: renderer.getPixelRatio() } : null, camera: camera?.position.toArray(), target: controls?.target.toArray(), meshes: sourceMeshes.length, inferredMeshes: sourceMeshes.filter((m) => ['historic', 'patio'].includes(m.userData.zone)).length }; } };
init().catch(fail);
