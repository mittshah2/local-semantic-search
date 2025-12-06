// --- Animation System (Factory Pattern) ---

class AnimationBase {
    init(scene) { }
    update() { }
    onSearch() { }
    onResize() { }
}

class BlackHoleAnimation extends AnimationBase {
    constructor() {
        super();
        this.stars = null;
        this.vortex = null;
        this.speedMultiplier = 1.0;
    }

    init(scene) {
        // Starfield
        const starGeo = new THREE.BufferGeometry();
        const starCount = 6000; // Increased count
        const posArray = new Float32Array(starCount * 3);

        for (let i = 0; i < starCount * 3; i++) {
            posArray[i] = (Math.random() - 0.5) * 2000;
        }

        starGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        const starMat = new THREE.PointsMaterial({
            size: 1.5,
            color: 0xffffff,
            transparent: true,
            opacity: 0.8
        });

        this.stars = new THREE.Points(starGeo, starMat);
        scene.add(this.stars);

        // No vortex/wireframe object - keeping it clean
    }

    update() {
        if (this.stars) {
            this.stars.rotation.z += 0.0002 * this.speedMultiplier;
            // Warp speed effect handling
            if (this.speedMultiplier > 1.0) {
                this.stars.rotation.z += 0.02;
                // Stretch effect via scale
                this.stars.scale.z = Math.min(this.stars.scale.z + 0.2, 5.0);
                this.speedMultiplier *= 0.96;
            } else {
                // Return to normal
                if (this.stars.scale.z > 1.05) {
                    this.stars.scale.z *= 0.95;
                } else {
                    this.stars.scale.z = 1.0;
                }
            }
        }
    }

    onSearch() {
        // Trigger warp speed
        this.speedMultiplier = 10.0;
    }
}

class AnimationFactory {
    static createAnimation(type) {
        switch (type) {
            case 'black_hole':
                return new BlackHoleAnimation();
            default:
                console.warn(`Animation type '${type}' not found.`);
                return new BlackHoleAnimation();
        }
    }
}

// --- Main Scene Manager ---

let scene, camera, renderer;
let currentAnimation = null;

function initThree() {
    const container = document.getElementById('canvas-container');

    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050510, 0.001);

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 3000);
    camera.position.z = 50;

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Initialize Animation Strategy
    currentAnimation = AnimationFactory.createAnimation('black_hole');
    currentAnimation.init(scene);

    window.addEventListener('resize', onWindowResize, false);
    animate();
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    if (currentAnimation) currentAnimation.onResize();
}

function animate() {
    requestAnimationFrame(animate);
    if (currentAnimation) currentAnimation.update();
    renderer.render(scene, camera);
}

// --- UI Logic ---

const searchInput = document.getElementById('search-input');
const uiContainer = document.querySelector('.ui-container');
const resultsContainer = document.getElementById('results-container');
const statusText = document.getElementById('status-text');

searchInput.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    }
});

function performSearch(query) {
    // 1. Trigger Animation
    if (currentAnimation) {
        currentAnimation.onSearch();
    }

    // 2. Call Backend
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.search(query).then(results => {
            displayResults(results);
        }).catch(err => {
            console.error(err);
            statusText.textContent = "Search Error: " + err;
            statusText.className = 'status-text error';
        });
    } else {
        console.warn("Pywebview API not found (running in browser?)");
    }
}

function displayResults(results) {
    resultsContainer.innerHTML = '';

    if (!results || results.length === 0) {
        resultsContainer.style.display = 'none';
        return;
    }

    resultsContainer.style.display = 'block';

    results.forEach(res => {
        const el = document.createElement('div');
        el.className = 'result-item';
        el.innerHTML = `
            <div class="result-name">${res.name}</div>
            <div class="result-path">${res.path}</div>
        `;
        el.addEventListener('click', () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.open_file(res.path);
            }
        });
        resultsContainer.appendChild(el);
    });
}

// --- Status Polling ---

function updateStatus() {
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.get_status().then(status => {
            if (status) {
                statusText.textContent = status;
                if (status.toLowerCase().includes("error")) {
                    statusText.className = 'status-text error';
                } else {
                    statusText.className = 'status-text';
                }
            }
        });
    }
}

// Start polling every second
setInterval(updateStatus, 1000);

// Initialize
initThree();
