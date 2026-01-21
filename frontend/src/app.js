/**
 * Interior Design System - Frontend Application
 * Single-page app with Three.js 3D viewer
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : '';  // Same origin in production

// Application State
const state = {
    sessionId: null,
    sceneState: null,
    file: null,
    apartmentType: '2bhk',
    isLoading: false,
    actionHistory: []
};

// Three.js Components
let scene, camera, renderer, controls, currentModel;

// DOM Elements
const elements = {
    status: document.getElementById('status'),
    uploadArea: document.getElementById('uploadArea'),
    layoutInput: document.getElementById('layoutInput'),
    uploadedPreview: document.getElementById('uploadedPreview'),
    previewImage: document.getElementById('previewImage'),
    clearUpload: document.getElementById('clearUpload'),
    generateBtn: document.getElementById('generateBtn'),
    promptSection: document.getElementById('promptSection'),
    promptInput: document.getElementById('promptInput'),
    applyPromptBtn: document.getElementById('applyPromptBtn'),
    historySection: document.getElementById('historySection'),
    actionHistory: document.getElementById('actionHistory'),
    viewer3d: document.getElementById('viewer3d'),
    viewerPlaceholder: document.getElementById('viewerPlaceholder'),
    viewerControls: document.getElementById('viewerControls'),
    resetViewBtn: document.getElementById('resetViewBtn'),
    topViewBtn: document.getElementById('topViewBtn'),
    frontViewBtn: document.getElementById('frontViewBtn'),
    screenshotBtn: document.getElementById('screenshotBtn'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    errorToast: document.getElementById('errorToast'),
    toastMessage: document.getElementById('toastMessage'),
    toastClose: document.getElementById('toastClose')
};

// ============================================================================
// INITIALIZATION
// ============================================================================

function init() {
    setupEventListeners();
    initThreeJS();
}

function setupEventListeners() {
    // Upload area
    elements.uploadArea.addEventListener('click', () => elements.layoutInput.click());
    elements.layoutInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.add('dragover');
    });
    elements.uploadArea.addEventListener('dragleave', () => {
        elements.uploadArea.classList.remove('dragover');
    });
    elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // Clear upload
    elements.clearUpload.addEventListener('click', clearUpload);

    // Apartment type
    document.querySelectorAll('input[name="apartmentType"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            state.apartmentType = e.target.value;
        });
    });

    // Generate button
    elements.generateBtn.addEventListener('click', generateInitialScene);

    // Prompt
    elements.applyPromptBtn.addEventListener('click', applyDesignPrompt);
    elements.promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            applyDesignPrompt();
        }
    });

    // Suggestions
    document.querySelectorAll('.suggestion').forEach(el => {
        el.addEventListener('click', () => {
            elements.promptInput.value = el.dataset.prompt;
            elements.promptInput.focus();
        });
    });

    // Viewer controls
    elements.resetViewBtn.addEventListener('click', resetCameraView);
    elements.topViewBtn.addEventListener('click', setTopView);
    elements.frontViewBtn.addEventListener('click', setFrontView);
    elements.screenshotBtn.addEventListener('click', takeScreenshot);

    // Toast close
    elements.toastClose.addEventListener('click', hideError);

    // Window resize
    window.addEventListener('resize', onWindowResize);
}

// ============================================================================
// THREE.JS SETUP
// ============================================================================

function initThreeJS() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    // Camera
    camera = new THREE.PerspectiveCamera(
        60,
        elements.viewer3d.clientWidth / elements.viewer3d.clientHeight,
        0.1,
        1000
    );
    camera.position.set(10, 10, 10);

    // Renderer - using WebGL with fallback settings for CPU
    renderer = new THREE.WebGLRenderer({
        antialias: true,
        powerPreference: 'low-power',  // Prefer integrated GPU/CPU
        failIfMajorPerformanceCaveat: false  // Don't fail on software rendering
    });
    renderer.setSize(elements.viewer3d.clientWidth, elements.viewer3d.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    // Don't append yet - wait until we have a model

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 2;
    controls.maxDistance = 50;
    controls.maxPolarAngle = Math.PI / 2;

    // Lighting
    setupLighting();

    // Grid helper (floor reference)
    const gridHelper = new THREE.GridHelper(20, 20, 0x444466, 0x333344);
    scene.add(gridHelper);

    // Animation loop
    animate();
}

function setupLighting() {
    // Ambient light
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambient);

    // Main directional light (sun)
    const directional = new THREE.DirectionalLight(0xffffff, 0.8);
    directional.position.set(10, 20, 10);
    directional.castShadow = true;
    directional.shadow.mapSize.width = 2048;
    directional.shadow.mapSize.height = 2048;
    directional.shadow.camera.near = 0.5;
    directional.shadow.camera.far = 50;
    directional.shadow.camera.left = -20;
    directional.shadow.camera.right = 20;
    directional.shadow.camera.top = 20;
    directional.shadow.camera.bottom = -20;
    scene.add(directional);

    // Fill light
    const fill = new THREE.DirectionalLight(0x8888ff, 0.3);
    fill.position.set(-10, 5, -10);
    scene.add(fill);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function onWindowResize() {
    if (!renderer.domElement.parentElement) return;

    const width = elements.viewer3d.clientWidth;
    const height = elements.viewer3d.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize(width, height);
}

// ============================================================================
// MODEL LOADING
// ============================================================================

async function loadModel(url) {
    const loader = new GLTFLoader();

    return new Promise((resolve, reject) => {
        loader.load(
            url,
            (gltf) => {
                // Remove previous model
                if (currentModel) {
                    scene.remove(currentModel);
                    disposeModel(currentModel);
                }

                currentModel = gltf.scene;

                // Enable shadows
                currentModel.traverse((child) => {
                    if (child.isMesh) {
                        child.castShadow = true;
                        child.receiveShadow = true;
                    }
                });

                scene.add(currentModel);

                // Center camera on model
                fitCameraToModel(currentModel);

                resolve(gltf);
            },
            (progress) => {
                const percent = (progress.loaded / progress.total * 100).toFixed(0);
                elements.loadingText.textContent = `Loading model... ${percent}%`;
            },
            reject
        );
    });
}

function disposeModel(model) {
    model.traverse((child) => {
        if (child.isMesh) {
            child.geometry.dispose();
            if (child.material.isMaterial) {
                cleanMaterial(child.material);
            } else if (Array.isArray(child.material)) {
                child.material.forEach(cleanMaterial);
            }
        }
    });
}

function cleanMaterial(material) {
    material.dispose();
    for (const key in material) {
        if (material[key] && typeof material[key].dispose === 'function') {
            material[key].dispose();
        }
    }
}

function fitCameraToModel(model) {
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    cameraZ *= 1.5; // Zoom out a bit

    camera.position.set(center.x + cameraZ * 0.5, center.y + cameraZ * 0.5, center.z + cameraZ);
    controls.target.copy(center);
    controls.update();
}

// ============================================================================
// CAMERA CONTROLS
// ============================================================================

function resetCameraView() {
    if (currentModel) {
        fitCameraToModel(currentModel);
    } else {
        camera.position.set(10, 10, 10);
        controls.target.set(0, 0, 0);
        controls.update();
    }
}

function setTopView() {
    const target = controls.target.clone();
    camera.position.set(target.x, target.y + 20, target.z);
    controls.update();
}

function setFrontView() {
    const target = controls.target.clone();
    camera.position.set(target.x, target.y + 3, target.z + 15);
    controls.update();
}

function takeScreenshot() {
    renderer.render(scene, camera);
    const dataURL = renderer.domElement.toDataURL('image/png');

    const link = document.createElement('a');
    link.download = `interior-design-${Date.now()}.png`;
    link.href = dataURL;
    link.click();
}

// ============================================================================
// FILE HANDLING
// ============================================================================

function handleFileSelect(e) {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
}

function handleFile(file) {
    // Validate file type
    const validTypes = ['image/png', 'image/svg+xml', 'image/jpeg'];
    if (!validTypes.includes(file.type)) {
        showError('Please upload a PNG, SVG, or JPG file');
        return;
    }

    state.file = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.previewImage.src = e.target.result;
        elements.uploadArea.style.display = 'none';
        elements.uploadedPreview.style.display = 'flex';
        elements.generateBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

function clearUpload() {
    state.file = null;
    elements.layoutInput.value = '';
    elements.uploadArea.style.display = 'block';
    elements.uploadedPreview.style.display = 'none';
    elements.generateBtn.disabled = true;
}

// ============================================================================
// API CALLS
// ============================================================================

async function generateInitialScene() {
    if (!state.file) {
        showError('Please upload a floor plan first');
        return;
    }

    showLoading('Generating 3D model...');

    try {
        const formData = new FormData();
        formData.append('file', state.file);
        formData.append('apartment_type', state.apartmentType);

        const response = await fetch(`${API_BASE_URL}/api/upload-layout`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate scene');
        }

        const data = await response.json();

        state.sessionId = data.session_id;
        state.sceneState = data.scene_state;

        // Load the 3D model
        const modelUrl = `${API_BASE_URL}${data.model_url}`;
        await loadModel(modelUrl);

        // Show viewer
        showViewer();

        // Enable prompt section
        elements.promptSection.style.display = 'block';

        setStatus('Model loaded', 'active');

    } catch (error) {
        console.error('Error generating scene:', error);
        showError(error.message);
        setStatus('Error', 'error');
    } finally {
        hideLoading();
    }
}

async function applyDesignPrompt() {
    const prompt = elements.promptInput.value.trim();

    if (!prompt) {
        showError('Please enter a design request');
        return;
    }

    if (!state.sessionId) {
        showError('Please generate a 3D model first');
        return;
    }

    showLoading('Applying design changes...');
    setStatus('Processing', 'processing');

    try {
        const response = await fetch(`${API_BASE_URL}/api/design`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: state.sessionId,
                prompt: prompt
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to apply changes');
        }

        const data = await response.json();

        if (!data.success) {
            showError(data.error || 'Request could not be processed');
            setStatus('Error', 'error');
            return;
        }

        // Update state
        state.sceneState = data.scene_state;

        // Load updated model
        const modelUrl = `${API_BASE_URL}${data.model_url}`;
        await loadModel(modelUrl);

        // Add to history
        addToHistory(prompt, data.actions_taken);

        // Clear prompt
        elements.promptInput.value = '';

        setStatus('Changes applied', 'active');

    } catch (error) {
        console.error('Error applying design:', error);
        showError(error.message);
        setStatus('Error', 'error');
    } finally {
        hideLoading();
    }
}

// ============================================================================
// UI HELPERS
// ============================================================================

function showViewer() {
    elements.viewerPlaceholder.style.display = 'none';
    elements.viewerControls.style.display = 'flex';

    // Append renderer to viewer
    if (!renderer.domElement.parentElement) {
        elements.viewer3d.appendChild(renderer.domElement);
        onWindowResize();
    }
}

function showLoading(message) {
    elements.loadingText.textContent = message;
    elements.loadingOverlay.style.display = 'flex';
    state.isLoading = true;
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
    state.isLoading = false;
}

function showError(message) {
    elements.toastMessage.textContent = message;
    elements.errorToast.style.display = 'flex';

    // Auto hide after 5 seconds
    setTimeout(hideError, 5000);
}

function hideError() {
    elements.errorToast.style.display = 'none';
}

function setStatus(text, className = '') {
    elements.status.textContent = text;
    elements.status.className = 'status';
    if (className) {
        elements.status.classList.add(className);
    }
}

function addToHistory(prompt, actions) {
    state.actionHistory.unshift({ prompt, actions, timestamp: new Date() });

    // Update UI
    elements.historySection.style.display = 'block';

    const li = document.createElement('li');
    li.textContent = prompt;
    elements.actionHistory.insertBefore(li, elements.actionHistory.firstChild);

    // Keep only last 10 items
    while (elements.actionHistory.children.length > 10) {
        elements.actionHistory.removeChild(elements.actionHistory.lastChild);
    }
}

// ============================================================================
// START APPLICATION
// ============================================================================

document.addEventListener('DOMContentLoaded', init);
